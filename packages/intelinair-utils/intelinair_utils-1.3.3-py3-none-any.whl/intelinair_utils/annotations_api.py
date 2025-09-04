import io
import json
import zipfile
from pathlib import Path
from typing import Dict, List, Union, Optional, Generator

import geojson
import shapely.geometry
from shapely.validation import make_valid

from intelinair_utils.agmri_api import AgmriApi

ANNOTATION_URL_TEMPLATE = 'https://api.{}.intelinair.dev/admin/graphql/index'


class AnnotationsApi:
    """Special API for annotation tool"""

    ANNOTATION_CRS = 4326

    def __init__(self, agmri_env: str, config_path: Optional[str] = None):
        """
        Args:
            agmri_env: the env name
            config_path: the optional path to agmri.cfg, if yoy want to use ssm, use ssm://<ssm param name>
        """
        self.api = AgmriApi(agmri_env, config_path=config_path)

    def list_annotation_types(self, api_limit_size: int = 100):
        offset = 0
        while True:
            query = f"""
            query {{ 
              listTagOptions( 
                max: {api_limit_size}
                offset: {offset} 
                queryCommand: {{
                  domain: "Annotation"
                }}
              ) {{ 
                results {{ 
                  id 
                  name 
                  description 
                  type {{
                    id
                    name
                    keyName
                    domainName
                    __typename
                  }}
                  color   
                  __typename 
                }} 
                totalCount 
                __typename 
              }} 
            }} 
            """

            response = self.api.graphql_request('admin', query=query)

            for tag_option in response['data']['listTagOptions']['results']:
                yield tag_option

            if api_limit_size + offset < response['data']['listTagOptions']['totalCount']:
                offset += api_limit_size
            else:
                break

    def get_annotation_project_by_name(self, name: str):
        query = f"""query {{getProject(name: \"{name}\") {{
              id
              name
              version
              description
              status
              flightsCount
              labels {{
                id
                version
                color
                createdBy
                dateCreated
                name
                description
                type {{
                  id
                  keyName
                  name
                }}
              }}
            }}
        }}
        """
        return self.api.graphql_request('admin', query)['data']['getProject']

    def create_annotation_project(self, name: str, description: str = "", label_ids: List[int] = None):
        """Create annotation project.

        Args:
            name: name of created project
            description: description for the project
            label_ids: labels used in the project

        Returns: integer project id

        """
        api_key = 'projectCreate'
        payload = f"""mutation {{
          {api_key}(project: {{
                        name: "{name}",
                        description : "{description}",
                        labelIds: {str([] if label_ids is None else label_ids)}
                                }}
                        )
                        {{
                            id
                            name
                            description
                            labelIds
                            status
                            errors {{
                                message
                            }}
                        }}
                    }}"""

        response = self._make_request(payload=payload, api_key=api_key)
        return response['data'][api_key]['id']

    def list_annotation_projects(self, api_limit_size=100):
        offset = 0
        while True:
            query = f"""
            query {{ 
              listProjects( 
                max: {api_limit_size} 
                offset: {offset} 
                queryCommand: {{}}
              ) {{ 
                results {{ 
                  id 
                  name 
                  description 
                  labels {{ 
                    id 
                    name 
                    color 
                    type {{ 
                      id 
                      domainName 
                      __typename 
                    }} 
                    __typename 
                  }} 
                  members {{ 
                    id 
                    user {{
                      id 
                      token 
                      firstname 
                      lastname 
                      __typename 
                    }} 
                    __typename 
                  }} 
                  status 
                  configs 
                  __typename 
                }} 
                totalCount 
                __typename 
              }} 
            }} 
            """

            response = self.api.graphql_request('admin', query=query)

            for project in response['data']['listProjects']['results']:
                yield project

            if api_limit_size + offset < response['data']['listProjects']['totalCount']:
                offset += api_limit_size
            else:
                break

    def delete_annotation_project(self, project_id: int):
        query = f"""
        mutation  {{
          projectDelete(id: {project_id}) {{
            success
            error
            __typename
          }}
        }}
        """

        response = self.api.graphql_request('admin', query=query)
        assert response['data']['projectDelete']['success'], 'Failed to delete project'

    def create_annotatable_flight(self, project_id: int, flight_id: int):
        """Create annotatable flight out of ordinary flight.

        Args:
            project_id: project in which to create annotatable flight
            flight_id: ordinary flight id

        Returns:
            id of created annotatable flight

        """
        api_key = 'annotatableFlightCreate'
        payload = f"""mutation {{
                  {api_key}(annotatableFlight: {{
                                project : {{
                                      id : {project_id}
                                    }}
                                flight : {{
                                     id : {flight_id}
                                    }}
                                }}
                  )
                  {{
                    id
                    errors {{
                        message
                    }}
                  }}
                }}"""
        response = self._make_request(payload=payload, api_key=api_key)
        return response['data'][api_key]['id']

    def list_annotatable_flights(self, project_id: int, api_limit_size: int = 100):
        offset = 0
        while True:
            query = f"""
            query {{
              listAnnotatableFlights( 
                max: {api_limit_size}
                offset: {offset} 
                queryCommand: {{
                  projectId: {project_id}
                }}
              ) {{ 
                results {{ 
                  id 
                  assignee {{
                    id
                    user {{
                      id
                      username
                      __typename
                    }}
                    __typename
                  }}
                  status
                  project {{
                    id
                    __typename
                  }}
                  flight {{
                    id
                    code
                    __typename
                  }}
                  notes
                  groupNumber   
                  __typename 
                }} 
                totalCount 
                __typename 
              }} 
            }} 
            """

            response = self.api.graphql_request('admin', query=query)

            for annotatable_flight in response['data']['listAnnotatableFlights']['results']:
                yield annotatable_flight

            if api_limit_size + offset < response['data']['listAnnotatableFlights']['totalCount']:
                offset += api_limit_size
            else:
                break

    def add_annotations(self, annotatable_flight_id: int, polygons: Dict, labels: List[str], color: str = "#FF9A34"):
        """Add annotation to annotatable flight.

        Args:
            annotatable_flight_id: id of flight to add annotation
            polygons: polygons to add as annotation
            labels: string annotation labels
            color: adding custom color if needed

        Returns:
            response from api call

        """
        api_key = "annotationCreate"
        valid_geom = geojson.dumps(polygons).replace('"', '\\"')

        payload = f"""
        mutation {{
          {api_key}(annotation: {{
              flight: {{
                  id: {annotatable_flight_id}
              }},
              color: "{color}"
              labels: {json.dumps(labels) if labels else []}
              geometry: "{valid_geom}" }})
        {{
            id
            labels
            errors {{
                message
            }}
          }}
        }}"""
        response = self._make_request(payload=payload, api_key=api_key)
        return response

    def get_annotations(self, project_id: int, flight_code: Optional[str] = None,
                        api_limit_size: int = 1000) -> Generator[dict, None, None]:
        """Get annotations from a project

        Args:
            project_id: The id of the project to get annotations from
            flight_code: optionally filter by a flight
            api_limit_size: string annotation labels

        Returns:
            response from api call

        """
        if not flight_code:
            query_command = f"{{projectId: {project_id}}}"
        else:
            query_command = f"{{projectId: {project_id}, flightCode: \"{flight_code}\"}}"
        offset = 0
        while True:
            payload = f"""
                {{
                    listAnnotations(
                        max: {api_limit_size},
                        offset: {offset},
                        queryCommand: {query_command}
                    )
                    {{
                        results {{
                            flight {{
                                status
                                flight {{
                                    code
                                    tags
                                }}
                            }}
                            labels
                            geometry
                        }}
                        totalCount
                    }}
                }} """
            response = self.api.graphql_request(service='admin', query=payload)
            for result in response['data']['listAnnotations']['results']:
                geometry = shapely.geometry.shape(json.loads(result["geometry"]))
                yield {
                    'flight_code': result['flight']['flight']['code'],
                    'status': result['flight']['status'],
                    'labels': result['labels'],
                    'geometry': make_valid(geometry),
                    'tags': result['flight']['flight']['tags']
                }
            offset += api_limit_size
            if offset >= response['data']['listAnnotations']['totalCount']:
                break

    def download_annotations(self, project_id: int, output_path: Union[str, Path]):
        response = self.api.post('/annotations/export', ignore_json=True, params={
            "projectId": project_id,
            "flightCode": None,
            "labelIds": None
        })

        annotations_zipfile = zipfile.ZipFile(io.BytesIO(response.content))
        assert len(annotations_zipfile.filelist) == 1
        annotations = annotations_zipfile.read(annotations_zipfile.filelist[0])
        with open(output_path, 'wb') as fp:
            fp.write(annotations)

    def _make_request(self, payload: str, api_key: str):
        """Make actual call to graphql with provided payload.

        Args:
            payload: request payload
            api_key: name of api in use

        Returns:

        """
        response = self.api.graphql_request(service='admin', query=payload)
        errors = response["errors"] if 'errors' in response else response["data"][api_key].get("errors")
        if errors:
            raise Exception(f'Errors while making api request to {api_key}: {errors}')
        return response
