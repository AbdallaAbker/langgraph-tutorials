#import libraries
from langgraph.graph import StateGraph, START, END
from typing import Dict, TypedDict, Optional, Literal, List, Union

# define the state
class GraphState(TypedDict):
    init_input: Optional[str] = None
    fruit: Optional[str] = None
    final_result: Optional[str] = None
    user_confirmation: Optional[str] = None  # New field for user confirmation

# Optional 
# is used to indicate that a value can either be of a specified type or be None. 
# It is a way to express that a variable or function return value might not have a value (i.e., it can be None).

### TypedDict
# is a type annotation construct introduced in Python 
# to allow for more precise type checking of dictionaries with a fixed set of keys, 
# each associated with specific value types. This is especially useful when dealing with structured data such as JSON responses from web APIs.

# Purpose: It helps ensure that dictionaries have specific keys with specific types of values.
# Example Use Case: When you receive JSON data from a web API and want to make sure it matches a particular structure.


# input_fruit: This function processes the initial input to validate if the fruit is in the predefined list. 
# It updates the state with the fruit name or sets an error.
def input_fruit(state: GraphState) -> Dict[str, str]:
    print("Node: input_fruit()")
    init_input = state.get("init_input", "").strip().lower()
    
    if init_input not in ["apple", "banana", "cherry"]:
        return {"fruit": "error"}
    
    return {"fruit": init_input}

# review_fruit: This function allows the user to review their fruit selection. 
# It doesn't modify the state, but it prints a review message.
def review_fruit(state: GraphState) -> Dict[str, str]:
    print("--------------------------")
    print("Node: review_fruit()")
    print(f"Review your selection: {state['fruit']}. Is this correct?")
    return {"fruit": state['fruit']}

# confirm_fruit: This function sets the final result when the fruit selection is confirmed by the user.
def confirm_fruit(state: GraphState) -> Dict[str, str]:
    print("--------------------------")
    print("Node: confirm_fruit()")
    return {"final_result": f"You selected {state['fruit']}, which is a valid fruit."}

#review_decision: This function determines the next node based on the user's confirmation after reviewing the fruit. 
# If the user confirms, it transitions to confirm_fruit; otherwise, it transitions to error.
def review_decision(state: GraphState) -> Literal["to_confirm_fruit", "to_error"]:
    print("--------------------------")
    print("Function Edge: review_decision:")
    print(f"Function Edge Continue: state: {state}")
    if state.get("user_confirmation") == "yes":
        print("Function Edge Continue: to_confirm_fruit")
        return "to_confirm_fruit"
    
    print("Function Edge Continue: to_error")
    return "to_error"


# continue_next: This modified function determines the next node based on the state after input_fruit. 
# If the fruit is valid, it transitions to review_fruit; otherwise, it transitions to error.
def continue_next(state: GraphState) -> Literal["to_review_fruit", "to_error"]:
    print("--------------------------")
    print("Function Edge: continue_next:")
    print(f"Function Edge State: {state}")
    if state.get("fruit") != "error":
        print("Function Edge Continue: to_review_fruit")
        return "to_review_fruit"
    
    print("Function Edge Continue: continue to_error")
    return "to_error"


# error: This function sets the final result to an error message if there is an error in the input 
# or the user rejects the selection.
def error(state: GraphState) -> Dict[str, str]:
    print("--------------------------")
    print("Node: error()")
    return {"final_result": "error"}



# Construct the workflow
workflow = StateGraph(GraphState)

workflow.add_node("input_fruit", input_fruit)
workflow.add_node("review_fruit", review_fruit)
workflow.add_node("confirm_fruit", confirm_fruit)
workflow.add_node("error", error)

workflow.set_entry_point("input_fruit")
workflow.add_edge("confirm_fruit", END)
workflow.add_edge("error", END)

workflow.add_conditional_edges(
    "input_fruit",  # The node where the decision is made
    continue_next,  # The function that makes the decision
    {    
        "to_review_fruit": "review_fruit",  # Mapping function output to nodes
        "to_error": "error",
    },
)

workflow.add_conditional_edges(
    "review_fruit",  # The node where the decision is made after review
    review_decision,  # The function that makes the decision after review
    {    
        "to_confirm_fruit": "confirm_fruit",  # Mapping function output to nodes
        "to_error": "error",
    },
)


app = workflow.compile()

app.get_graph().draw_mermaid_png(output_file_path="fruit-graph-with-user-feedback.png")


################################ Test with 3 Cases ####################################

# Test with a valid fruit and user confirmation
result = app.invoke({"init_input": "apple", "user_confirmation": "yes"})
print("Result:")
print(result)


# Test with a valid fruit and user rejection (simulate error for simplicity)
result = app.invoke({"init_input": "apple", "user_confirmation": "no"})
print("Result:")
print(result)


# Test with an invalid fruit
result = app.invoke({"init_input": "mango"})
print("Result:")
print(result)