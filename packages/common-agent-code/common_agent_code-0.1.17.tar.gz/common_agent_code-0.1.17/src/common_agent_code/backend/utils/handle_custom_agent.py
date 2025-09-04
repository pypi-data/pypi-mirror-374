from flask import jsonify
from common_agent_code.backend.models import ChatHistory
from common_agent_code.backend import db
import json
import traceback
from common_agent_code.backend.utils.execute_code import execute_code
from common_agent_code.backend.utils.AgentState import AgentState
from common_agent_code.backend.utils.get_model_completion import get_model_completion

def handle_custom_agent(conversation_id, message, definition, file_path=None, preserved_objects={}, system_prompt_override=None):
    try:
        print(f"Starting custom agent handler for conversation {conversation_id}")

        plot_paths_accumulated = []
        system_prompt = system_prompt_override or definition.system_prompt
        
        system_prompt += (
            "\n\nIMPORTANT: Your response MUST be a JSON object. "
            "Your main goal is to solve the user's request step-by-step. "
            "If you need to write and execute code, provide it in the 'code' field. "
            "After execution, I will provide you with the output and errors. "
            "Based on that feedback, you will plan your next step."
            "🔒 SYSTEM REQUIREMENT 🔒 : FIRST UNDERSTAND WHAT IS IN THE OBJECT for e.g if DF then do df.columns(), df.head(), df.describe() etc."
            "🔒 SYSTEM REQUIREMENT 🔒 : You MUST re-use the returned_objects dictionary already present in memory if it exists, instead of reinitializing it. Do not use returned_objects = {} if one is already available."
            "🔒 SYSTEM REQUIREMENT 🔒 : When saving plots, you MUST save them to the 'static' folder using os.makedirs('static', exist_ok=True') AND record the file path into returned_objects['plot_paths']"
            "🔒 SYSTEM REQUIREMENT 🔒 : Make sure no spaces are there in the file path"
            "🔒 SYSTEM REQUIREMENT 🔒 : Make sure the plot paths are added to returned_objects using returned_objects.setdefault('plot_paths', []).append(path)"
            "🔒 SYSTEM REQUIREMENT 🔒 : VERY IMPORTANTTTTTT: If you want to print, you can't think it acts like a notebook. YOU HAVE TO PRINT IT by calling print and other relevant functions!"
            "🔒 SYSTEM REQUIREMENT 🔒 : Variables are NOT automatically displayed - you MUST use print() to show them to the user!"
            "🔒 SYSTEM REQUIREMENT 🔒 : This IS a persistent session — previous code cells DO persist. All functions and variables from previous executions are available."
            
            "\n\n🔐 STATE PERSISTENCE RULES:"
            "• ONLY data stored in 'returned_objects' will persist between API calls"
            "• Variables created outside returned_objects will be LOST after execution"
            "• Store important data like: returned_objects['analysis_results'] = results"
            "• Store DataFrames as: returned_objects['df'] = dataframe"
            "• Store metrics as: returned_objects['metrics'] = {'key': value}"
            
            "\n\n📊 DATA DISPLAY RULES:"
            "• Variables are NOT automatically displayed - you MUST use print() to show them"
            "• To display a DataFrame: print(df.head()) or print(df.describe())"
            "• To display results: print('Results:', results)"
            "• To display metrics: print('Metrics:', json.dumps(metrics, indent=2))"
            "• Always print important findings so the user can see them"
            
            "\n\n💾 RECOMMENDED DATA STORAGE PATTERN:"
            "```python"
            "# Store analysis results"
            "returned_objects['analysis_results'] = analysis_results"
            "returned_objects['metrics'] = metrics"
            "returned_objects['investment_plan'] = investment_plan"
            ""
            "# Display results to user"
            "print('Analysis Results:')"
            "print(json.dumps(analysis_results, indent=2))"
            "print('Investment Plan:')"
            "print(json.dumps(investment_plan, indent=2))"
            "```"
            
            "\n\nJSON Structure:"
            "{\n"
            "  \"reasoning\": \"Your thought process and explanation for EACH step. ***DO NOT use 'updated_answer' or any other key. This is the only supported explanation key***\",\n"
            "  \"code\": \"The Python code to execute for this step. (can be an empty string)\",\n"
            "  \"is_complete\": boolean (Set to true ONLY when the final answer is ready and all tasks are done.)\n"
            "}\n"
        ) 
    
        messages = [{"role": "system", "content": system_prompt}]

        # Helpers to sanitize objects before saving to DB to avoid recursion errors
        def _is_preservable_local(x):
            try:
                if x is None or isinstance(x, (str, bool, int, float)):
                    return True
                if isinstance(x, list):
                    return all(_is_preservable_local(i) for i in x)
                if isinstance(x, dict):
                    return all(isinstance(k, str) and _is_preservable_local(v) for k, v in x.items())
                import pandas as pd
                import numpy as np
                if isinstance(x, (pd.DataFrame, pd.Series, np.ndarray)):
                    return True
                import pickle
                try:
                    pickle.dumps(x)
                    return True
                except Exception:
                    return False
            except Exception:
                return False

        def _sanitize_mapping(mapping):
            safe = {}
            if isinstance(mapping, dict):
                for k, v in mapping.items():
                    if isinstance(k, str) and _is_preservable_local(v):
                        safe[k] = v
            return safe

        # Load previous state from database if it exists
        if conversation_id:
            try:
                latest_message = ChatHistory.query.filter_by(
                    conversation_id=conversation_id,
                    agent_type='custom'
                ).filter(ChatHistory.pickled_objects.isnot(None)).order_by(
                    ChatHistory.timestamp.desc()
                ).first()
                
                if latest_message:
                    loaded_objects = latest_message.load_objects()
                    if loaded_objects:
                        # Merge loaded objects with preserved_objects
                        preserved_objects.update(loaded_objects)
                        print(f"✅ Restored state from database: {list(loaded_objects.keys())}")
            except Exception as e:
                print(f"⚠️ Warning: Could not restore previous state: {e}")

        if preserved_objects:
            available_vars = ", ".join(preserved_objects.keys())
            initial_state_message = (
                f"The following variables have been restored/loaded and are available for use: {available_vars}. "
                "These are already loaded in memory - DO NOT reload them from files. "
                "**IMPORTANT AND REQUIRED** - Start by inspecting them (e.g., with `.head()`, `.columns`, `.info()`) to understand their structure before proceeding."
            )
            messages.append({"role": "system", "content": initial_state_message})
            
        conversation_history = ChatHistory.query.filter(
            ChatHistory.conversation_id == conversation_id,
            ChatHistory.role.in_(["user", "assistant"])
        ).order_by(ChatHistory.timestamp).all()

        for msg in conversation_history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": message})

        not_complete = True
        final_answer = None
        reasoning_steps = []
        count = 0
        max_iterations = 15

        # Initialize state with preserved objects
        state = AgentState(initial_data=preserved_objects.copy())
        
        while not_complete and count < max_iterations:
            count += 1
            raw_output = get_model_completion(messages, definition.model_type)

            try:
                output_json = json.loads(raw_output)
            except json.JSONDecodeError:
                # Handle JSON parsing error
                messages.append({"role": "assistant", "content": raw_output})
                messages.append({"role": "user", "content": "Error: Your last response was not valid JSON. Please correct it and adhere to the specified JSON format."})
                continue
            print(f"🔍 Model output JSON: {output_json}")
            is_complete = output_json.get('is_complete', False)
            reasoning = output_json.get("reasoning") or output_json.get("updated_answer", "")
            code_to_execute = output_json.get('code', '')
            
            # Initialize execution result variables
            execution_output, execution_error = "", ""
            execution_result = None
            plot_paths = []
            
            # Add assistant message to conversation
            messages.append({"role": "assistant", "content": raw_output})
            
            if code_to_execute:
                print("⚙️ Executing code...")
                print(f"Code to execute:\n{code_to_execute}")
                execution_result = execute_code(code_to_execute, state)
                print(f'Execution result is : {execution_result}')
                execution_output = execution_result.output
                execution_error = execution_result.error
                
                # Collect all plot paths over multiple iterations
                persisted_returned = preserved_objects.get("returned_objects", {})
                persisted_paths = persisted_returned.get("plot_paths", [])
                new_paths = execution_result.returned_objects.get("plot_paths", [])
                merged_paths = list(dict.fromkeys(persisted_paths + new_paths))
                persisted_returned["plot_paths"] = merged_paths
                preserved_objects["returned_objects"] = persisted_returned
                plot_paths_accumulated = merged_paths
                print(plot_paths_accumulated)
                
                # Update the main state with any new or modified variables from the execution
                preserved_objects.update(state.data) 
                print(f"State updated. Current variables: {list(preserved_objects.keys())}")
                
                # Automatically save state after each execution if memory is enabled
                if definition.memory_enabled:
                    try:
                        memory_message = ChatHistory(
                            conversation_id=conversation_id,
                            agent_type="custom",
                            model_type=definition.model_type,
                            agent_definition_id=definition.id,
                            role="system",
                            content=f"State updated after execution. Variables: {list(preserved_objects.keys())}"
                        )
                        # Save only sanitized returned_objects to avoid recursion issues
                        ro = preserved_objects.get("returned_objects", {}) if isinstance(preserved_objects, dict) else {}
                        memory_message.save_objects(_sanitize_mapping(ro))
                        db.session.add(memory_message)
                        db.session.commit()
                        print("💾 State automatically saved after execution.")
                    except Exception as e:
                        print(f"⚠️ Warning: Could not save state: {e}")
                
                # Provide feedback to the model
                feedback = (
                    f"Your code has been executed.\n"
                    f"Output (stdout):\n---\n{execution_output or 'No output'}\n---\n"
                    f"Error:\n---\n{execution_error or 'None'}\n---\n"
                )
                if execution_error:
                    feedback += "The code failed. Please analyze the error and provide the corrected code. Do NOT repeat the failed code."
                else:
                    feedback += "The code executed successfully. Please proceed to the next step or conclude the task."
                messages.append({"role": "user", "content": feedback})
                
            # Prepare response content with safe defaults
            response_content = {
                "updated_answer": reasoning,
                "code": code_to_execute,
                "is_complete": is_complete,
                "output": execution_output,
                "error": execution_error,
                "plot_paths": plot_paths_accumulated
            }
            ai_message = ChatHistory(
                conversation_id=conversation_id,
                agent_type="custom",
                model_type=definition.model_type,
                agent_definition_id=definition.id,
                role="assistant",
                content=json.dumps(response_content),
                code=code_to_execute,
                step_number=count
            )

            # Persist safe objects on the assistant message so clients can fetch them immediately after the call
            objects_to_save = {}
            if execution_result and isinstance(execution_result.returned_objects, dict):
                objects_to_save.update(execution_result.returned_objects)
            existing_ro = preserved_objects.get("returned_objects") if isinstance(preserved_objects, dict) else None
            if isinstance(existing_ro, dict):
                objects_to_save.update(existing_ro)
            objects_to_save = _sanitize_mapping(objects_to_save)
            if objects_to_save:
                ai_message.save_objects(objects_to_save)

            db.session.add(ai_message)
            db.session.commit()

            reasoning_steps.append({
                "step_number": count,
                "reasoning": reasoning,
                "next_step": output_json.get('next_step', ''),
                "code": code_to_execute,
                "output": execution_output,
                "error": execution_error,
                "plot_paths": plot_paths_accumulated
            })
            print(reasoning)
            if is_complete:
                if not plot_paths_accumulated:
                    final_returned = preserved_objects.get("returned_objects", {})
                    if "plot_paths" in final_returned:
                        plot_paths_accumulated.extend(final_returned["plot_paths"])
                final_answer = {
                    "reasoning": "FINAL ANSWER:\n\n" + reasoning,
                    "code_to_execute": code_to_execute,
                    "final_output": execution_output,
                    "plot_paths": plot_paths_accumulated
                }
                not_complete = False

        # Final state persistence (always save at the end if memory is enabled)
        if definition.memory_enabled and preserved_objects:
            try:
                memory_message = ChatHistory(
                    conversation_id=conversation_id,
                    agent_type="custom",
                    model_type=definition.model_type,
                    agent_definition_id=definition.id,
                    role="system",
                    content="Final state saved at end of conversation"
                )
                ro = preserved_objects.get("returned_objects", {}) if isinstance(preserved_objects, dict) else {}
                memory_message.save_objects(_sanitize_mapping(ro))
                db.session.add(memory_message)
                db.session.commit()
                print("💾 Final state saved successfully.")
            except Exception as e:
                print(f"⚠️ Warning: Could not save final state: {e}")

        print(f"Custom agent handler completed. Is complete: {not not_complete}")
        
        result = {
            "reasoning_steps": reasoning_steps,
            "final_output": final_answer,
            "preserved_objects": list(preserved_objects.keys()) if preserved_objects else [],
            "plot_paths": plot_paths_accumulated,
            "system_prompt_used": system_prompt
        }
        print('Plot Paths:', plot_paths_accumulated)
        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        print(f"Error in handle_custom_agent: {e}")
        return jsonify({"error": f"Error in custom agent: {str(e)}"}), 500

def _is_sanitizable(obj):
    """Check if an object can be safely serialized (prevents recursion)"""
    import pandas as pd
    import numpy as np
    
    # ✅ Safe: Primitive types
    if isinstance(obj, (str, int, float, bool, type(None))):
        return True
        
    # ✅ Safe: Lists and dicts of primitives
    if isinstance(obj, list):
        return all(_is_sanitizable(item) for item in obj)
    if isinstance(obj, dict):
        return all(isinstance(k, str) and _is_sanitizable(v) for k, v in obj.items())
        
    # ✅ Safe: Pandas DataFrames (convert to dict)
    if isinstance(obj, pd.DataFrame):
        return True
        
    # ✅ Safe: Numpy arrays (convert to list)
    if isinstance(obj, np.ndarray):
        return True
        
    # ❌ Dangerous: Functions, classes, API clients, complex objects
    if callable(obj) or hasattr(obj, '__dict__'):
        return False
        
    # ❌ Dangerous: Objects that might have circular references
    try:
        import pickle
        pickle.dumps(obj)
        return True
    except (pickle.PickleError, RecursionError, TypeError):
        return False
    