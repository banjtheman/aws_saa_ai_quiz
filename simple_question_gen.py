# Python imports
import os
from typing import Type, Union, Dict, Any, List
import pickle

# 3rd party imports
import pandas as pd
import numpy as np
import utils
import random
import openai
import tiktoken



# Set open AI Key
openai.api_key = os.environ["OPEN_AI_KEY"]
EMBEDDING_MODEL = "text-embedding-ada-002"


# Content DataFrame
DF = pd.read_csv("min_aws_wa.csv")

# Document Embeddings
with open("document_embeddings.pkl", "rb") as file:
    # Call load method to deserialze
    DOC_EMBEDS = pickle.load(file)


scenarios = [
    "A large corporation wants to move their on-premises compute to the cloud for increased scalability and security.",
    "A startup wants to host their new web application on AWS.",
    "A company has a critical application that needs to be up at all times",
    "A media company wants to store large amounts of data that will be used for thier applications",
    "A financial services company wants to run a highly available and secure infrastructure to process financial transactions.",
    "A healthcare company wants to store and process sensitive patient information in the cloud.",
    "A company wants to run batch processing jobs on AWS, but wants to minimize costs when the jobs are not running.",
    "A company wants to build a mobile application that needs to access and store data in the cloud.",
    "A company wants to store log files from their applications for analysis and compliance purposes.",
    "A company wants to run a disaster recovery plan for their critical systems on AWS.",
    "A gaming company wants to use AWS to host and scale their multiplayer game servers.",
    "A retail company wants to leverage AWS to support their e-commerce platform during peak shopping seasons.",
    "A research institution wants to perform data analysis on a large dataset using AWS compute resources.",
    "A software development team wants to build and deploy a microservices-based application on AWS.",
    "A marketing company wants to use AWS to process and analyze large volumes of customer data for targeted advertising campaigns.",
    "An education organization wants to use AWS to deliver online learning courses to students globally.",
    "A transportation company wants to use AWS to process real-time data from connected vehicles to optimize their operations.",
    "A social media platform wants to use AWS to store and process user-generated content.",
    "A telecommunications company wants to use AWS to host and manage their network infrastructure.",
    "A manufacturing company wants to use AWS to optimize their supply chain and production processes.",
]

domains = utils.load_json("domain_array.json")
# domains = utils.load_json("domains.json")


def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> list[float]:
    result = openai.Embedding.create(model=model, input=text)
    return result["data"][0]["embedding"]


def vector_similarity(x: list[float], y: list[float]) -> float:
    """
    Returns the similarity between two vectors.

    Because OpenAI Embeddings are normalized to length 1, the cosine similarity is the same as the dot product.
    """
    return np.dot(np.array(x), np.array(y))


def order_document_sections_by_query_similarity(
    query: str, contexts: dict[(str, str), np.array]
) -> list[(float, (str, str))]:
    """
    Find the query embedding for the supplied query, and compare it against all of the pre-calculated document embeddings
    to find the most relevant sections.

    Return the list of document sections, sorted by relevance in descending order.
    """
    query_embedding = get_embedding(query)

    document_similarities = sorted(
        [
            (vector_similarity(query_embedding, doc_embedding), doc_index)
            for doc_index, doc_embedding in contexts.items()
        ],
        reverse=True,
    )

    return document_similarities


MAX_SECTION_LEN = 1500
SEPARATOR = "\n* "
ENCODING = "cl100k_base"  # encoding for text-embedding-ada-002

encoding = tiktoken.get_encoding(ENCODING)
separator_len = len(encoding.encode(SEPARATOR))

def construct_prompt(
    question: str, scenario: str, context_embeddings: dict, df: pd.DataFrame
) -> str:
    """
    Fetch relevant
    """
    most_relevant_document_sections = order_document_sections_by_query_similarity(
        question, context_embeddings
    )

    chosen_sections = []
    chosen_sections_len = 0
    chosen_sections_indexes = []

    for _, section_index in most_relevant_document_sections:
        # Add contexts until we run out of space.
        print(section_index)
        document_section = df.loc[
            (df["title"] == section_index[0]) & (df["url"] == section_index[1])
        ]

        # Location of values
        num_tokens = document_section.values[0][3]
        curr_text = document_section.values[0][2]

        chosen_sections_len += +num_tokens + separator_len
        if chosen_sections_len > MAX_SECTION_LEN:
            break

        chosen_sections.append(SEPARATOR + curr_text.replace("\n", " "))
        chosen_sections_indexes.append(str(section_index))

    # Useful diagnostic information
    # print(f"Selected {len(chosen_sections)} document sections:")
    # print("\n".join(chosen_sections_indexes))

    context = "".join(chosen_sections)
    header = f"""Generate a scenario-based multiple-choice question for the AWS Certified Solutions Architect Associate Exam using the provided scenario, context, and knowledge area. The response must be returned in the specified JSON format with nothing else. There should be one correct answer and 3 incorrect answers. The incorrect answers should be response options that a candidate with incomplete knowledge or skill might choose. Provide an explanation for the answer to each question as well. The question must be about a scenario, and not a simple definition question such as What type of storage is Amazon S3. The answers must also be action-oriented and not just the name of a service.\n\nScenario:\n{scenario}`"\n\nContext:\n"""
    return (
        (
            header
            + context
            + "\n\nKnowledge Area: "
            + question
            + '\n\nJSON Format:\n{"question": "","answer_choices": [{"answer": "","is_correct": "","explanation": ""},{"answer": "","is_correct": "","explanation": ""},{"answer": "","is_correct": "","explanation": ""},{"answer": "","is_correct": "","explanation": ""}]}\n'
        ),
        context,
        chosen_sections_indexes,
    )


def generate_question_chatgpt(
    query: str,
    scenario: str,
    df: pd.DataFrame,
    document_embeddings: dict[(str, str), np.array],
    show_prompt: bool = False,
) -> str:
    (
        prompt,
        context,
        docs,
    ) = construct_prompt(query, scenario, document_embeddings, df)

    if show_prompt:
        print(prompt)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an AWS Certified Solutions Architect Associate Exam Question Generation Bot. Your role is to generate a scenario-based multiple-choice question for the AWS Certified Solutions Architect Associate Exam using the scenario, context and JSON format provided by the user. The response must be returned in the specified JSON format with nothing else. There should be one correct answer and 3 incorrect answers. The incorrect answers should be response options that a candidate with incomplete knowledge or skill might choose. Provide an explanation for the answer to each question as well. The question must be about a scenario, and not a simple definition question such as What type of storage is Amazon S3. The answers must also be action-oriented and not just the name of a service.",
            },
            {
                "role": "user",
                "content": f"""\n\nScenario:\n{scenario}`"\n\nContext:\n{context}"""
                + '\n\nJSON format:\n{"question": "","answer_choices": [{"answer": "","is_correct": "","explanation": ""},{"answer": "","is_correct": "","explanation": ""},{"answer": "","is_correct": "","explanation": ""},{"answer": "","is_correct": "","explanation": ""}]}\n',
            },
        ],
    )

    # print(response)
    # question = response["choices"][0]["text"].strip(" \n")
    question = response["choices"][0]["message"]["content"].strip(" \n")

    return prompt, question, docs


def gen_question_chatgpt(scenario, domain_obj):
    """
    Purpose:
        Generate a Question
    Args:
        scenario: scenario to use
        domain_obj: domain_obj with data
    Returns:
        question_json - JSON of question details
    """

    task = domain_obj["task"]
    domain = domain_obj["domain"]
    focus = domain_obj["focus"]
    item = domain_obj["item"]

    prompt, question, docs = generate_question_chatgpt(
        item, scenario, DF, DOC_EMBEDS, False
    )

    try:
        question_text = question[question.index("{") :]
    except:
        question_text = question

    question_json = {}
    question_json["scenario"] = scenario
    question_json["domain"] = domain
    question_json["task"] = task
    question_json["focus"] = focus
    question_json["item"] = item
    question_json["prompt"] = prompt
    question_json["question"] = question_text
    question_json["docs"] = docs

    return question_json


def main() -> None:
    """
    Purpose:
        Controls the flow of the app
    Args:
        N/A
    Returns:
        N/A
    """

    print("Generating questions")

    # We want to create one question for each item in the domains
    num_items = len(domains["domain_list"]) - 1

    domain_list = domains["domain_list"]

    question_list = []

    for index, item_obj in enumerate(domain_list):
        item_name = item_obj["item"]
        print(f"Working on item: {item_name} ({index}/{num_items})")
        rand_scenario = random.choice(scenarios)

        question_json = gen_question_chatgpt(rand_scenario, item_obj)
        # Add to list
        question_list.append(question_json)

    # Save questions in JSON object
    final_json = {"question_list": question_list}

    # utils.save_json("full_ai_gen_questions.json", final_json)


if __name__ == "__main__":
    main()
