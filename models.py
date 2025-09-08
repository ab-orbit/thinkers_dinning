from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PhilosophicalStatement(BaseModel):
    content: str = Field(description="The philosophical statement text")
    iteration: int = Field(description="Current iteration number")
    timestamp: datetime = Field(default_factory=datetime.now)


class Assessment(BaseModel):
    overview: str = Field(description="General assessment overview of the statement")
    strengths: List[str] = Field(description="List of identified strengths")
    weaknesses: List[str] = Field(description="List of critical weaknesses")
    ranking: int = Field(ge=1, le=10, description="Numerical ranking from 1 (weakest) to 10 (strongest)")
    reasoning: str = Field(description="Detailed reasoning behind the ranking")
    timestamp: datetime = Field(default_factory=datetime.now)


class InteractionLog(BaseModel):
    iteration: int
    statement: PhilosophicalStatement
    assessment: Optional[Assessment] = None
    agent_response: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class WorkflowSession(BaseModel):
    session_id: str
    initial_statement: str
    current_statement: str
    current_iteration: int = Field(default=0)
    max_iterations: int = Field(default=100)
    target_ranking: int = Field(default=10)
    interactions: List[InteractionLog] = Field(default_factory=list)
    completed: bool = Field(default=False)
    final_ranking: Optional[int] = None
    completion_reason: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class AphoristicorResponse(BaseModel):
    refined_statement: str = Field(description="The refined philosophical statement")
    explanation: str = Field(description="Explanation of changes made based on assessment")
    iteration: int = Field(description="Current iteration number")


class AssessorResponse(BaseModel):
    assessment: Assessment = Field(description="Detailed assessment of the statement")
    ready_for_next: bool = Field(description="Whether ready for next iteration or workflow completion")