"""
Purpose:
    Start AWS Quiz
"""

# Python imports
import json
from typing import Type, Union, Dict, Any, List
import random
from urllib.request import urlopen

# 3rd party imports
import streamlit as st
import utils


# List of Questions
@st.cache_data
def load_questions():
    url = "https://raw.githubusercontent.com/banjtheman/aws_saa_ai_quiz/main/trim_aws_ai_gen_questions.json"
    response = urlopen(url)

    question_list = json.loads(response.read())["question_list"]
    # question_list = utils.load_json("trim_aws_ai_gen_questions.json")["question_list"] # File too big to load?

    # Randomize list
    random.shuffle(question_list)

    return question_list


# Map questions to chocies
index_map = {0: "A: ", 1: "B: ", 2: "C: ", 3: "D: "}


def sidebar() -> None:
    """
    Purpose:
        Shows the side bar
    Args:
        N/A
    Returns:
        N/A
    """

    st.sidebar.image(
        "https://d1.awsstatic.com/training-and-certification/certification-badges/AWS-Certified-Solutions-Architect-Associate_badge.3419559c682629072f1eb968d59dea0741772c0f.png",
        use_column_width=True,
    )

    st.sidebar.markdown(
        "The AWS Certified Solutions Architect - Associate AI Generated Quiz is a tool designed to help individuals prepare for the exam. It uses GPT-3 to generate scenario-based multiple choice questions and provides a comprehensive explanation for the correct answer as well as resources."
    )


def gen_quiz(question_obj, question, show_scenario, key="my-form"):
    form = st.form(key=key)

    ans_list = question_obj["answer_choices"]
    choice_list = []
    correct_list = []
    exp_list = []

    scenario = question["scenario"]

    if show_scenario:
        q_string = f"Scenario: {scenario}\n\nQuestion: {question_obj['question']}"
    else:
        q_string = question_obj["question"]

    for choice in ans_list:
        choice_list.append(choice["answer"])
        correct_list.append(choice["is_correct"])
        exp_list.append(choice["explanation"])

    selected_answer = form.radio(q_string, choice_list)
    submit = form.form_submit_button("Submit")

    curr_index = choice_list.index(selected_answer)

    if submit:
        # Check if correct
        curr_index = choice_list.index(selected_answer)

        if str(correct_list[curr_index]).lower() == "true":
            st.success("Correct! " + index_map[curr_index] + choice_list[curr_index])
            st.write(exp_list[curr_index])

            with st.expander("Explanations"):
                for index, item in enumerate(exp_list):
                    if index == curr_index:
                        continue
                    st.error(index_map[index] + choice_list[index])
                    st.write(item)
        else:
            st.error("Wrong! " + index_map[curr_index] + choice_list[curr_index])
            st.write(exp_list[curr_index])

            with st.expander("Explanations"):
                for index, item in enumerate(exp_list):
                    if index == curr_index:
                        continue

                    elif str(correct_list[index]).lower() == "true":
                        st.success(index_map[index] + choice_list[index])
                        st.write(item)

                    else:
                        st.error(index_map[index] + choice_list[index])
                        st.write(item)

        # Show resoucres
        with st.expander("Resources"):
            domain = question["domain"]
            task = question["task"]
            focus = question["focus"]
            item = question["item"]

            st.subheader(domain)
            st.write(task)
            st.write(focus + ": " + item)

            for doc in question["docs"]:
                st.write(doc)

        with st.expander("Prompt"):
            prompt = question["prompt"]
            st.write(prompt)


def app() -> None:
    """
    Purpose:
        Controls the app flow
    Args:
        N/A
    Returns:
        N/A
    """

    # Spin up the sidebar
    sidebar()
    # Load questions
    question_list = load_questions()

    curr_question = st.number_input(
        "Question Number:", min_value=0, max_value=len(question_list) - 1
    )

    # Get question details
    question = question_list[curr_question]
    question_json = json.loads(question["question"])

    # Checkbox for scenario
    show_scenario = st.checkbox(
        "Show Scenario?", help="Shows the scenario used to generate the question"
    )

    # Generate the quiz
    gen_quiz(question_json, question, show_scenario)


def main() -> None:
    """
    Purpose:
        Controls the flow of the streamlit app
    Args:
        N/A
    Returns:
        N/A
    """

    # Start the streamlit app
    st.title("AWS Certified Solutions Architect - Associate AI Generated Quiz")
    st.subheader("Study Smarter, Not Harder")
    app()


if __name__ == "__main__":
    main()
