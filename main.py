#!/usr/bin/env python3
"""
Thinkers Dinning - Philosophical Statement Refinement Workflow

An agentic system where two AI agents collaborate to iteratively refine
philosophical statements through critical assessment and improvement.

Agents:
- Aphoristicor (OpenAI): Creates and refines philosophical statements
- Assessor (Anthropic): Critically evaluates statements from epistemological 
  and scientific reasoning perspectives

The workflow continues until the statement achieves a ranking of 10/10 
or reaches the maximum number of iterations (100).
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from workflow import PhilosophicalRefinementWorkflow


def setup_environment():
    """Load environment variables and validate API keys."""
    load_dotenv()
    
    required_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    missing_keys = []
    
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        print("❌ Missing required environment variables:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\nPlease set these in your .env file (see .env.example)")
        sys.exit(1)
    
    print("✅ Environment configuration validated")


def main():
    """Main entry point for the philosophical refinement workflow."""
    
    print("🧠 Thinkers Dinning - Philosophical Statement Refinement")
    print("=" * 60)
    
    # Setup environment
    setup_environment()
    
    # Get input statement
    if len(sys.argv) > 1:
        statement = " ".join(sys.argv[1:])
    else:
        print("\nEnter a philosophical statement to refine:")
        statement = input("> ").strip()
        
        if not statement:
            # Use default test statement
            statement = "Reality is as complex as the human [in]capacity to comprehend it"
            print(f"Using default test statement: '{statement}'")
    
    print(f"\n📝 Processing statement: '{statement}'")
    
    # Initialize and run workflow
    try:
        workflow = PhilosophicalRefinementWorkflow(
            max_iterations=100,
            target_ranking=10
        )
        
        result = workflow.run(statement)
        
        # Print final results
        print("\n" + "="*80)
        print("🎉 WORKFLOW COMPLETED")
        print("="*80)
        print(f"Session ID: {result.session_id}")
        print(f"Total Iterations: {result.current_iteration}")
        print(f"Final Ranking: {result.final_ranking}/10")
        print(f"Completion Reason: {result.completion_reason}")
        print(f"\nInitial Statement:")
        print(f'  "{result.initial_statement}"')
        print(f"\nFinal Statement:")
        print(f'  "{result.current_statement}"')
        
        if result.final_ranking and result.final_ranking >= result.target_ranking:
            print(f"\n🎯 SUCCESS: Target ranking achieved!")
        else:
            print(f"\n⏰ Process ended without reaching target ranking")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error running workflow: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()