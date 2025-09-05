"""Main file for entrypoint to package"""

import logging
import re

import requests
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.capabilitystatement import CapabilityStatement
from fhir.resources.R4B.fhirtypes import Id
from fhir.resources.R4B.operationoutcome import OperationOutcome
from requests import Session, Response
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from .helpers.capabilitystatement import get_supported_search_params, load_capability_statement
from .helpers.conditionhelper import expand_condition_onset_in_bundle
from .helpers.documenthelper import expand_document_references_in_bundle
from .helpers.fhirfilter import filter_bundle
from .helpers.gapanalysis import run_gap_analysis
from .helpers.medicationhelper import expand_medication_references_in_bundle
from .models.models import CustomFormatter, QuerySearchParams, SupportedSearchParams

logger: logging.Logger = logging.getLogger("fhirsearchhelper")
logger.setLevel(logging.INFO)
ch: logging.StreamHandler = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

# Epic IDs are sometimes more than the max_length of 64 set in the default
Id.configure_constraints(max_length=256)


def run_fhir_query(
    base_url: str = None,  # type: ignore
    query_headers: dict[str, str] = None,  # type: ignore
    search_params: QuerySearchParams = None,  # type: ignore
    query: str | None = None,
    capability_statement_file: str | None = None,
    capability_statement_url: str | None = None,
    debug: bool = False,
) -> Bundle | OperationOutcome | None:
    """
    Entry function to run FHIR query using a CapabilityStatement and returning filtered resources
    WARNING: There is currently not a way to use a CapabilityStatement out of the box. See README.md of source for details.
    """

    if debug:
        logger.info("Logging level is being set to DEBUG")
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)

    # Error handling
    if not base_url and not search_params and not query:
        raise ValueError("You must provide either a base_url and a dictionary of search parameters or the full query string in the form of <baseUrl>/<resourceType>?<param1>=<value1>&...")

    session: Session = Session()
    retries: Retry = Retry(total=5, allowed_methods={"GET", "POST", "PUT", "DELETE"}, status_forcelist=[500])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.mount("http://", HTTPAdapter(max_retries=retries))

    cap_state: CapabilityStatement = load_capability_statement(session=session, url=capability_statement_url, file_path=capability_statement_file)
    supported_search_params: list[SupportedSearchParams] = get_supported_search_params(cap_state)

    pretty_supported_search_params: dict[str, list[str]] = {
        resource_params["resourceType"]: [item["name"] for item in resource_params["searchParams"]] for resource_params in [item.dict(exclude_none=True) for item in supported_search_params]
    }

    logger.debug(f"Supported search parameters for this server are: {pretty_supported_search_params}")

    if query:
        url_res, q_search_params = query.split("?")
        if url_res.split("/")[-1] not in pretty_supported_search_params:
            logger.error(f'Resource {url_res.split("/")[-1]} is not supported for searching, returning empty Bundle')
            return Bundle(**{"type": "searchset", "total": 0, "link": [{"relation": "self", "url": url_res}]})
        if not q_search_params:
            logger.error("No search params, Epic does not support pulling all resources of a given type with no search parameters. Please refine your query.")
            new_query_response: Response = session.get(f"{url_res}", headers=query_headers)
            if new_query_response.status_code == 403:
                logger.error(f"The query responded with a status code of {new_query_response.status_code}")
                if "WWW-Authenticate" in new_query_response.headers:
                    logger.error(f'WWW-Authenticate Error: {new_query_response.headers["WWW-Authenticate"]}')
                    OO_body = {
                        "resourceType": "OperationOutcome",
                        "issue": [{"severity": "error", "code": "processing", "diagnostics": f'WWW-Authenticate Error: {new_query_response.headers["WWW-Authenticate"]}'}],
                    }
                else:
                    OO_body: dict = {
                        "resourceType": "OperationOutcome",
                        "issue": [{"severity": "error", "code": "processing", "diagnostics": f"The query responded with a status code of {new_query_response.status_code}"}],
                    }
                return OperationOutcome(**OO_body)
            elif new_query_response.status_code == 400:
                return OperationOutcome(**new_query_response.json())
            else:
                return None

        base_url = "/".join(url_res.split("/")[:-1])
        q_resource_type = url_res.split("/")[-1]
        search_params_list: list[str] = q_search_params.split("&")
        search_params_dict: dict[str, str] = {item.split("=")[0]: item.split("=")[1] for item in search_params_list}
        search_params: QuerySearchParams = QuerySearchParams(resourceType=q_resource_type, searchParams=search_params_dict)

    logger.info(f"Search parameters for this request are: {search_params}")

    gap_output: list[str] = run_gap_analysis(supported_search_params=supported_search_params, query_search_params=search_params)

    logger.debug(f"Gap output from these two sets of search parameters is: {gap_output}")

    new_query_params_str: str = "&".join([f"{key}={value}" for key, value in search_params.searchParams.items() if key not in gap_output])
    if new_query_params_str:
        new_query_string: str = f"{search_params.resourceType}?{new_query_params_str}"
    else:
        new_query_string = search_params.resourceType

    logger.debug(f"New query string is {new_query_string}")

    logger.info(f"Making request to {base_url}/{new_query_string}")
    new_query_response = session.get(f"{base_url}/{new_query_string}", headers=query_headers)
    if new_query_response.status_code == 400:
        logger.warning(
            "The query responded with a status code of 400 Bad Request. Most likely this is due to using an incorrect codesystem when searching a code on a resource. "
            "For example, searching CPT or HCPCS codes (Procedure codes) on an Observation. This will return an empty Bundle, but make sure to modify your queries to "
            "only search appropriate codes for the type of resource."
        )
        return Bundle(**{"type": "searchset", "total": 0, "link": [{"relation": "self", "url": f"{base_url}/{new_query_string}"}]})
    if new_query_response.status_code != 200:
        logger.error(f"The query responded with a status code of {new_query_response.status_code}")
        if "WWW-Authenticate" in new_query_response.headers:
            logger.error(f'WWW-Authenticate Error: {new_query_response.headers["WWW-Authenticate"]}')
            return OperationOutcome(
                **{
                    "resourceType": "OperationOutcome",
                    "issue": [{"severity": "error", "code": "processing", "diagnostics": f'WWW-Authenticate Error: {new_query_response.headers["WWW-Authenticate"]}'}],
                }
            )
        try:
            return new_query_response.json()
        except requests.exceptions.JSONDecodeError:
            if "html" in new_query_response.headers["Content-Type"]:
                logger.error("Error caused HTML response")
                title_match: re.Match[str] | None = re.search(r"<title>(.*?)</title>", new_query_response.text)
                if title_match:
                    title_content = title_match.group(1)  # Extract the content within the title tags
                    logger.error(f"Response error from query: {title_content}")
                    return OperationOutcome(**{"resourceType": "OperationOutcome", "issue": [{"severity": "error", "code": "processing", "diagnostics": "From Epic: " + title_content}]})
            logger.error("Unable to parse response as JSON body")
            return OperationOutcome(
                **{"resourceType": "OperationOutcome", "issue": [{"severity": "error", "code": "processing", "diagnostics": "Unable to parse response as JSON or HTML with a title"}]}
            )

    new_query_response_json: dict = new_query_response.json()

    try:
        if new_query_response_json["entry"][0]["resource"]["resourceType"] == "Patient":
            # Handling for empty lines in Patient.address
            if "address" in new_query_response_json["entry"][0]["resource"]:
                new_addresses: list[dict] = []
                for address in new_query_response_json["entry"][0]["resource"]["address"]:
                    address["line"] = [line for line in address["line"] if line]
                    new_addresses.append(address)
                new_query_response_json["entry"][0]["resource"]["address"] = new_addresses
    except (IndexError, KeyError):
        pass

    new_query_response_bundle: Bundle = Bundle.parse_obj(new_query_response_json)

    if not new_query_response_bundle.entry:
        return new_query_response_bundle

    return_resource_types = [entry.resource.resource_type.lower() for entry in new_query_response_bundle.entry]  # type: ignore

    if "operationoutcome" in return_resource_types:
        if all([item == "operationoutcome" for item in return_resource_types]):
            logger.warning("There was only OperationOutcomes in the return Bundle. Bundle.entry will be empty. See below for collected diagnostics or details strings:")
            collected_log_strings = list(set([(issue.diagnostics if issue.diagnostics else issue.details.text if issue.details and issue.details.text else None) for entry in new_query_response_bundle.entry for issue in entry.resource.issue])) #type: ignore
            logger.warning(collected_log_strings)
            new_query_response_bundle.entry = []
        else:
            logger.warning("There was at least one OperationOutcome in the return Bundle. See below for collected diagnostics or details strings:")
            oo_resources = list(filter(lambda x: x.resource_type == "OperationOutcome", [entry.resource for entry in new_query_response_bundle.entry]))  # type: ignore
            collected_log_strings = list(set([(issue.diagnostics if issue.diagnostics else issue.details.text if issue.details and issue.details.text else None) for entry in oo_resources for issue in entry.issue])) #type: ignore
            logger.warning(collected_log_strings)
            new_query_response_bundle.entry = list(filter(lambda x: x.resource.resource_type != "OperationOutcome", new_query_response_bundle.entry))  # type: ignore

    # This happens before since its searching on code which is completed by this expansion
    if "MedicationRequest" in new_query_string:
        logger.info("Resources are of type MedicationRequest, proceeding to expand MedicationReferences")
        new_query_response_bundle = expand_medication_references_in_bundle(session=session, input_bundle=new_query_response_bundle, base_url=base_url, query_headers=query_headers)

    logger.debug(f"Size of bundle before filtering is {new_query_response_bundle.total} resources")
    filtered_bundle: Bundle = filter_bundle(input_bundle=new_query_response_bundle, search_params=search_params, gap_analysis_output=gap_output)
    logger.info(f"Size of bundle after filtering is {filtered_bundle.total} resources")

    output_bundle = filtered_bundle

    if "DocumentReference" in new_query_string:
        logger.info("Resources are of type DocumentReference, proceeding to expand DocumentReferences")
        output_bundle = expand_document_references_in_bundle(session=session, input_bundle=filtered_bundle, base_url=base_url, query_headers=query_headers)
    elif "Condition" in new_query_string:
        logger.info("Resources are of type Condition, checking if any are Encounter Diagnoses...")
        if "encounter-diagnosis" in [category.coding[0].code for entry in filtered_bundle.entry for category in entry.resource.category]:  # type: ignore
            logger.info("Found Condition resources with category Encounter Diagnosis, proceeding to extract Encounter.period.start as Condition.onsetDateTime")
            output_bundle = expand_condition_onset_in_bundle(session=session, input_bundle=filtered_bundle, base_url=base_url, query_headers=query_headers)

    return output_bundle
