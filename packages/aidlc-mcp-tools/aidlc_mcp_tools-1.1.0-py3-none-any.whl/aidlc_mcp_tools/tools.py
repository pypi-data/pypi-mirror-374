"""
AIDLC Dashboard MCP Tools Implementation

Provides MCP tools for AI agents to automatically sync project progress
with the AIDLC Dashboard service.
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MCPToolResult:
    """Result of an MCP tool execution."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AIDLCDashboardMCPTools:
    """MCP Tools for AIDLC Dashboard integration."""
    
    def __init__(self, base_url: str = None, 
                 timeout: int = 30, retry_attempts: int = 3):
        """
        Initialize AIDLC Dashboard MCP Tools.
        
        Args:
            base_url: Base URL of the AIDLC Dashboard API (defaults to env var or localhost)
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts for failed requests
        """
        # Use environment variable if base_url not provided
        if base_url is None:
            base_url = os.getenv('AIDLC_BASE_URL', 'http://localhost:8000/api')
        
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AIDLC-MCP-Tools/1.0.3'
        })
        
        logger.info(f"Initialized AIDLC MCP Tools with base URL: {base_url}")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> MCPToolResult:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request data for POST/PUT requests
            
        Returns:
            MCPToolResult with success status and response data
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.retry_attempts):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=self.timeout)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=data, timeout=self.timeout)
                elif method.upper() == 'PUT':
                    response = self.session.put(url, json=data, timeout=self.timeout)
                elif method.upper() == 'DELETE':
                    response = self.session.delete(url, timeout=self.timeout)
                else:
                    return MCPToolResult(success=False, error=f"Unsupported HTTP method: {method}")
                
                # Check if request was successful
                if response.status_code in [200, 201]:
                    try:
                        return MCPToolResult(success=True, data=response.json())
                    except json.JSONDecodeError:
                        return MCPToolResult(success=True, data={"message": response.text})
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    if attempt == self.retry_attempts - 1:
                        return MCPToolResult(success=False, error=error_msg)
                    logger.warning(f"Request failed (attempt {attempt + 1}): {error_msg}")
                    time.sleep(1)  # Wait before retry
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"Request exception: {str(e)}"
                if attempt == self.retry_attempts - 1:
                    return MCPToolResult(success=False, error=error_msg)
                logger.warning(f"Request failed (attempt {attempt + 1}): {error_msg}")
                time.sleep(1)  # Wait before retry
        
        return MCPToolResult(success=False, error="Max retry attempts exceeded")
    
    def aidlc_health_check(self) -> MCPToolResult:
        """
        Check dashboard service health and connectivity.
        
        Returns:
            MCPToolResult with health status
        """
        logger.info("Performing health check")
        return self._make_request("GET", "/health")
    
    def aidlc_create_project(self, name: str, description: str = "") -> MCPToolResult:
        """
        Create a new project in the AIDLC Dashboard.
        
        Args:
            name: Project name
            description: Optional project description
            
        Returns:
            MCPToolResult with project creation result
        """
        logger.info(f"Creating project: {name}")
        
        data = {
            "name": name,
            "description": description
        }
        
        result = self._make_request("POST", "/projects", data)
        
        if result.success and result.data:
            # Extract project ID for easier access
            if "data" in result.data and "project" in result.data["data"]:
                project_id = result.data["data"]["project"]["id"]
                result.data["project_id"] = project_id
                logger.info(f"Project created successfully: {project_id}")
        
        return result
    
    def aidlc_get_project_status(self, project_id: str) -> MCPToolResult:
        """
        Retrieve current project status and progress.
        
        Args:
            project_id: Project identifier
            
        Returns:
            MCPToolResult with project info and progress details
        """
        logger.info(f"Getting project status: {project_id}")
        return self._make_request("GET", f"/projects/{project_id}")
    
    def aidlc_upload_epics(self, project_id: str, epics: List[Dict[str, Any]]) -> MCPToolResult:
        """
        Upload generated epics to a project.
        
        Args:
            project_id: Target project identifier
            epics: List of epic objects
            
        Returns:
            MCPToolResult with upload results
        """
        logger.info(f"Uploading {len(epics)} epics as individual artifacts to project {project_id}")
        
        uploaded_epics = []
        
        # Upload each epic as a separate artifact
        for i, epic in enumerate(epics):
            try:
                data = {
                    "artifact_type": "epics",
                    "content": epic  # Upload individual epic directly
                }
                
                result = self._make_request("POST", f"/projects/{project_id}/artifacts", data)
                
                if result.success:
                    epic_title = epic.get('title', f'Epic {i+1}')
                    logger.info(f"Successfully uploaded epic: {epic_title}")
                    
                    uploaded_epics.append({
                        "epic_index": i,
                        "epic_title": epic_title,
                        "artifact_id": result.data.get("data", {}).get("artifact", {}).get("id") if result.data else None
                    })
                else:
                    logger.error(f"Failed to upload epic {i+1}: {result.error}")
                    return MCPToolResult(
                        success=False, 
                        error=f"Failed to upload epic {i+1}: {result.error}"
                    )
                    
            except Exception as e:
                logger.error(f"Exception uploading epic {i+1}: {e}")
                return MCPToolResult(
                    success=False, 
                    error=f"Exception uploading epic {i+1}: {str(e)}"
                )
        
        # Update epics status to in-progress
        status_result = self.aidlc_update_artifact_status(project_id, "epics", "in-progress")
        if not status_result.success:
            logger.warning(f"Failed to update epics status: {status_result.error}")
        else:
            logger.info("Updating epics status to in-progress for project " + project_id)
        
        return MCPToolResult(
            success=True,
            data={
                "uploaded_epics": uploaded_epics,
                "total_count": len(uploaded_epics),
                "message": f"Successfully uploaded {len(uploaded_epics)} epics as individual artifacts"
            }
        )
    
    def aidlc_upload_user_stories(self, project_id: str, user_stories: List[Dict[str, Any]]) -> MCPToolResult:
        """
        Upload generated user stories to a project.
        
        Args:
            project_id: Target project identifier
            user_stories: List of user story objects
            
        Returns:
            MCPToolResult with upload results
        """
        logger.info(f"Uploading {len(user_stories)} user stories as individual artifacts to project {project_id}")
        
        uploaded_stories = []
        
        # Upload each user story as a separate artifact
        for i, story in enumerate(user_stories):
            try:
                # Fix field name: API expects 'story_id' not 'id'
                story_content = story.copy()
                if 'id' in story_content and 'story_id' not in story_content:
                    story_content['story_id'] = story_content.pop('id')

                data = {
                    "artifact_type": "user-stories",
                    "content": story_content  # Upload individual story with correct field name
                }
                
                result = self._make_request("POST", f"/projects/{project_id}/artifacts", data)
                
                if result.success:
                    story_title = story.get('title', f'Story {i+1}')
                    logger.info(f"Successfully uploaded user story: {story_title}")
                    
                    uploaded_stories.append({
                        "story_index": i,
                        "story_title": story_title,
                        "artifact_id": result.data.get("data", {}).get("artifact", {}).get("id") if result.data else None
                    })
                else:
                    logger.error(f"Failed to upload user story {i+1}: {result.error}")
                    return MCPToolResult(
                        success=False, 
                        error=f"Failed to upload user story {i+1}: {result.error}"
                    )
                    
            except Exception as e:
                logger.error(f"Exception uploading user story {i+1}: {e}")
                return MCPToolResult(
                    success=False, 
                    error=f"Exception uploading user story {i+1}: {str(e)}"
                )
        
        # Update user stories status to in-progress
        status_result = self.aidlc_update_artifact_status(project_id, "user-stories", "in-progress")
        if not status_result.success:
            logger.warning(f"Failed to update user stories status: {status_result.error}")
        
        return MCPToolResult(
            success=True,
            data={
                "uploaded_stories": uploaded_stories,
                "total_count": len(uploaded_stories),
                "message": f"Successfully uploaded {len(uploaded_stories)} user stories as individual artifacts"
            }
        )
    
    def aidlc_upload_domain_model(self, project_id: str, domain_entities: List[Dict[str, Any]], title: str = "", description: str = "") -> MCPToolResult:
        """
        Upload domain model entities to a project.
        
        Args:
            project_id: Target project identifier
            domain_entities: List of domain entity objects
            title: Optional overall title for the domain model
            description: Optional overall description for the domain model
            
        Returns:
            MCPToolResult with upload results
        """
        logger.info(f"Uploading domain model with {len(domain_entities)} entities to project {project_id}")
        
        try:
            # Fix field names and prepare entities
            processed_entities = []
            for entity in domain_entities:
                entity_content = entity.copy()
                if 'id' in entity_content and 'entity_id' not in entity_content:
                    entity_content['entity_id'] = entity_content.pop('id')
                processed_entities.append(entity_content)
            
            # Create complete domain model structure
            domain_model = {
                "entities": processed_entities,
                "relationships": [],  # Can be extended later
                "business_rules": []  # Can be extended later
            }
            
            # Add overall title and description if provided
            if title:
                domain_model["title"] = title
            if description:
                domain_model["description"] = description
            elif processed_entities:
                # Generate description from entities if not provided
                entity_names = [entity.get('name', 'Entity') for entity in processed_entities]
                domain_model["description"] = f"Domain model containing {len(processed_entities)} entities: {', '.join(entity_names)}"
            
            data = {
                "artifact_type": "domain-model",
                "content": domain_model
            }
            
            result = self._make_request("POST", f"/projects/{project_id}/artifacts", data)
            
            if result.success:
                logger.info("Successfully uploaded domain model")
                
                # Update domain model status to in-progress
                status_result = self.aidlc_update_artifact_status(project_id, "domain-model", "in-progress")
                if not status_result.success:
                    logger.warning(f"Failed to update domain model status: {status_result.error}")
                
                return MCPToolResult(
                    success=True,
                    data={
                        "message": f"Successfully uploaded domain model with {len(processed_entities)} entities",
                        "entity_count": len(processed_entities),
                        "artifact_id": result.data.get("data", {}).get("artifact", {}).get("id") if result.data else None
                    }
                )
            else:
                logger.error(f"Failed to upload domain model: {result.error}")
                return result
                
        except Exception as e:
            logger.error(f"Exception uploading domain model: {e}")
            return MCPToolResult(
                success=False, 
                error=f"Exception uploading domain model: {str(e)}"
            )
    
    def aidlc_upload_model_code_plan(self, project_id: str, code_phases: List[Dict[str, Any]]) -> MCPToolResult:
        """
        Upload model code plan phases to a project.
        
        Args:
            project_id: Target project identifier
            code_phases: List of code plan phase objects
            
        Returns:
            MCPToolResult with upload results
        """
        logger.info(f"Uploading {len(code_phases)} code plan phases as individual artifacts to project {project_id}")
        
        uploaded_phases = []
        
        # Upload each code phase as a separate artifact
        for i, phase in enumerate(code_phases):
            try:
                # Fix field name: API expects appropriate field names
                phase_content = phase.copy()
                if 'id' in phase_content and 'phase_id' not in phase_content:
                    phase_content['phase_id'] = phase_content.pop('id')

                data = {
                    "artifact_type": "model-code-plan",
                    "content": phase_content  # Upload individual phase with correct field name
                }
                
                result = self._make_request("POST", f"/projects/{project_id}/artifacts", data)
                
                if result.success:
                    phase_name = phase.get('name', phase.get('component_name', f'Phase {i+1}'))
                    logger.info(f"Successfully uploaded code plan phase: {phase_name}")
                    
                    uploaded_phases.append({
                        "phase_index": i,
                        "phase_name": phase_name,
                        "artifact_id": result.data.get("data", {}).get("artifact", {}).get("id") if result.data else None
                    })
                else:
                    logger.error(f"Failed to upload code plan phase {i+1}: {result.error}")
                    return MCPToolResult(
                        success=False, 
                        error=f"Failed to upload code plan phase {i+1}: {result.error}"
                    )
                    
            except Exception as e:
                logger.error(f"Exception uploading code plan phase {i+1}: {e}")
                return MCPToolResult(
                    success=False, 
                    error=f"Exception uploading code plan phase {i+1}: {str(e)}"
                )
        
        # Update model code plan status to in-progress
        status_result = self.aidlc_update_artifact_status(project_id, "model-code-plan", "in-progress")
        if not status_result.success:
            logger.warning(f"Failed to update model code plan status: {status_result.error}")
        
        return MCPToolResult(
            success=True,
            data={
                "uploaded_phases": uploaded_phases,
                "total_count": len(uploaded_phases),
                "message": f"Successfully uploaded {len(uploaded_phases)} code plan phases as individual artifacts"
            }
        )
    
    def aidlc_upload_ui_code_plan(self, project_id: str, ui_code_plan: Dict[str, Any]) -> MCPToolResult:
        """
        Upload UI code plan to a project.
        
        Args:
            project_id: Target project identifier
            ui_code_plan: UI code plan object
            
        Returns:
            MCPToolResult with upload results
        """
        logger.info(f"Uploading UI code plan to project {project_id}")
        
        try:
            # Fix field name: API expects appropriate field names
            ui_plan_content = ui_code_plan.copy()
            if 'id' in ui_plan_content and 'plan_id' not in ui_plan_content:
                ui_plan_content['plan_id'] = ui_plan_content.pop('id')
            # Ensure plan_id and title are preserved if they exist
            # (The copy() already preserves them, this is just for clarity)

            data = {
                "artifact_type": "ui-code-plan",
                "content": ui_plan_content
            }
            
            result = self._make_request("POST", f"/projects/{project_id}/artifacts", data)
            
            if result.success:
                logger.info("Successfully uploaded UI code plan")
                
                # Update UI code plan status to in-progress
                status_result = self.aidlc_update_artifact_status(project_id, "ui-code-plan", "in-progress")
                if not status_result.success:
                    logger.warning(f"Failed to update UI code plan status: {status_result.error}")
                
                return MCPToolResult(
                    success=True,
                    data={
                        "message": "Successfully uploaded UI code plan",
                        "artifact_id": result.data.get("data", {}).get("artifact", {}).get("id") if result.data else None
                    }
                )
            else:
                logger.error(f"Failed to upload UI code plan: {result.error}")
                return result
                
        except Exception as e:
            logger.error(f"Exception uploading UI code plan: {e}")
            return MCPToolResult(
                success=False, 
                error=f"Exception uploading UI code plan: {str(e)}"
            )
    
    def aidlc_update_artifact_status(self, project_id: str, artifact_type: str, 
                                   status: str, notes: str = "") -> MCPToolResult:
        """
        Update artifact completion status.
        
        Args:
            project_id: Project identifier
            artifact_type: Type of artifact to update
            status: New status (not-started, in-progress, completed)
            notes: Optional status update notes
            
        Returns:
            MCPToolResult with status update result
        """
        logger.info(f"Updating {artifact_type} status to {status} for project {project_id}")
        
        data = {
            "artifact_type": artifact_type,
            "status": status
        }
        
        if notes:
            data["notes"] = notes
        
        return self._make_request("PUT", f"/projects/{project_id}/status", data)
