import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from agno.workflow import Workflow
from agents import AphoristicorAgent, AssessorAgent
from models import (
    WorkflowSession, InteractionLog, PhilosophicalStatement, 
    Assessment, AphoristicorResponse, AssessorResponse
)
from logger import MarkdownLogger


class PhilosophicalRefinementWorkflow:
    def __init__(self, max_iterations: int = 100, target_ranking: int = 10):
        self.workflow = Workflow(
            name="Philosophical Statement Refinement",
            description="Iterative refinement of philosophical statements through agentic collaboration",
            debug_mode=True
        )
        self.aphoristicor = AphoristicorAgent()
        self.assessor = AssessorAgent()
        self.max_iterations = max_iterations
        self.target_ranking = target_ranking
        self.logger = MarkdownLogger()
        
    def run(self, initial_statement: str) -> WorkflowSession:
        session_id = str(uuid.uuid4())[:8]
        
        session = WorkflowSession(
            session_id=session_id,
            initial_statement=initial_statement,
            current_statement=initial_statement,
            max_iterations=self.max_iterations,
            target_ranking=self.target_ranking
        )
        
        # Initialize markdown log
        log_filename = self._generate_log_filename(initial_statement)
        self.logger.initialize_log(log_filename, session)
        
        print(f"\n🚀 Starting Philosophical Refinement Workflow")
        print(f"Session ID: {session_id}")
        print(f"Initial Statement: '{initial_statement}'")
        print(f"Target Ranking: {self.target_ranking}/10")
        print(f"Max Iterations: {self.max_iterations}")
        print(f"Log File: {log_filename}")
        print("-" * 80)
        
        current_statement = initial_statement
        
        for iteration in range(1, self.max_iterations + 1):
            print(f"\n🔄 Iteration {iteration}")
            session.current_iteration = iteration
            
            # Create interaction log entry
            interaction = InteractionLog(
                iteration=iteration,
                statement=PhilosophicalStatement(
                    content=current_statement,
                    iteration=iteration
                )
            )
            
            # Step 1: Assessor evaluates the statement
            print(f"🧠 Assessor evaluating statement...")
            try:
                assessor_response: AssessorResponse = self.assessor.assess_statement(
                    current_statement, iteration
                )
                assessment = assessor_response.assessment
                interaction.assessment = assessment
                
                print(f"📊 Assessment Result:")
                print(f"   Ranking: {assessment.ranking}/10")
                print(f"   Strengths: {len(assessment.strengths)} identified")
                print(f"   Weaknesses: {len(assessment.weaknesses)} identified")
                
                # Log the assessment
                self.logger.log_assessment(assessment, iteration)
                
                # Check if target reached
                if assessment.ranking >= self.target_ranking:
                    session.completed = True
                    session.final_ranking = assessment.ranking
                    session.completion_reason = f"Target ranking {self.target_ranking} achieved"
                    session.completed_at = datetime.now()
                    
                    print(f"\n🎯 TARGET ACHIEVED!")
                    print(f"Final ranking: {assessment.ranking}/10")
                    print(f"Iterations completed: {iteration}")
                    
                    session.interactions.append(interaction)
                    self.logger.log_completion(session)
                    return session
                
            except Exception as e:
                print(f"❌ Error in assessment: {str(e)}")
                interaction.agent_response = f"Assessment error: {str(e)}"
                session.interactions.append(interaction)
                continue
            
            # Step 2: Aphoristicor refines the statement
            print(f"✏️  Aphoristicor refining statement...")
            try:
                aphoristicor_response: AphoristicorResponse = self.aphoristicor.refine_statement(
                    current_statement, assessment, iteration
                )
                
                refined_statement = aphoristicor_response.refined_statement
                interaction.agent_response = aphoristicor_response.explanation
                
                print(f"📝 Statement refined")
                print(f"   Original: '{current_statement[:60]}...'")
                print(f"   Refined:  '{refined_statement[:60]}...'")
                
                # Log the refinement
                self.logger.log_refinement(aphoristicor_response, iteration)
                
                current_statement = refined_statement
                session.current_statement = current_statement
                
            except Exception as e:
                print(f"❌ Error in refinement: {str(e)}")
                interaction.agent_response = f"Refinement error: {str(e)}"
                
            session.interactions.append(interaction)
            
            # Log the interaction
            self.logger.log_interaction(interaction)
        
        # Max iterations reached
        session.completed = True
        session.completion_reason = f"Maximum iterations ({self.max_iterations}) reached"
        session.completed_at = datetime.now()
        
        print(f"\n⏰ Maximum iterations reached ({self.max_iterations})")
        print(f"Final statement: '{session.current_statement}'")
        
        self.logger.log_completion(session)
        return session
    
    def _generate_log_filename(self, statement: str) -> str:
        # Create a descriptive filename from the statement
        words = statement.lower().split()
        # Take first few meaningful words, clean them up
        meaningful_words = [
            word.replace('[', '').replace(']', '').replace('(', '').replace(')', '')
            for word in words[:4] if len(word) > 2
        ]
        name_part = '_'.join(meaningful_words)
        
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{name_part}_{timestamp}.md"


if __name__ == "__main__":
    # Test with the provided statement
    workflow = PhilosophicalRefinementWorkflow()
    
    test_statement = "Reality is as complex as the human [in]capacity to comprehend it"
    
    result = workflow.run(test_statement)
    
    print(f"\n{'='*80}")
    print("WORKFLOW COMPLETED")
    print(f"{'='*80}")
    print(f"Session ID: {result.session_id}")
    print(f"Iterations: {result.current_iteration}")
    print(f"Final Ranking: {result.final_ranking}")
    print(f"Completion Reason: {result.completion_reason}")
    print(f"Final Statement: '{result.current_statement}'")