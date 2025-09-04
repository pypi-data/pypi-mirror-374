"""Prompt templates for video summarization tasks."""

REFINED_SUMMARY_CHUCKED_PROMPT = """
    You are given a portion of a youtube transcript with timestamps.
    The timestamps are placed in the begining of sentences in the
    format [%H:%M:%S or %M:%S (timestamp in seconds)].

    Create a very detailed and comphrensive summary of the topics in this section with their corresponding timestamps.
    Keep the examples and analogies if any.

    FORMATTING RULES:
    - Extract timestamps from [timestamp] markers
    - Format each point as: [timestamp] Summary text
    - Focus on main topics, arguments, and examples
    - Be comprehensive
    - Only include the start timestamp for each key point.
    - Ignore sponsor blocks

    Transcript section:
        {chunk}

    Here is the timestamped summary of key points from this section:
"""


REFINED_CONSOLIDATION_PROMPT = """
    You are given the metadata and multiple timestamped summaries from different sections
    of a video transcript which are overlaped.
    Organize and consolidate these into a coherent, comprehensive summary.

    RULES:
    1. Format the output as marked down with headers and bullet points.
    2. Give the Youtube metada at the top as a **list**, including: title, author, channel id, url, channel url,
        thumbnail url, language.
    3. Give an overall summary of the transcript.
    4. Breakdown into sections and subsections with bullet points for topics. Each bullet point
        should be a summary of a broad topic instead of an one-liner.
    5. Omit adjacent timestamps that refer to the same topic.
    6. Remove any redundancy
    7. Maintain chronological order
    8. Provide a Q&A section at the end with insightful questions and their answers based on the transcript.
    9. Add line breaks immediately after headers and subheaders.

    OUTPUT STRUCTURE:

    # Author: Video Title
    ## Metadata
        - title
        - author
        - channel id
        - url
        - channel url
        - thumbnail url
        - language

    ## Summary

    ## Sections
    ### Subsection 1
        - [timestamp 1] topic 1 for Header 1
        - [timestamp 2] topic 2 for Header 1
        - etc.
    ### Subsection 2
        - [timestamp 3] topic 1 for Header 2
        - etc.
    - etc.

    ## Q&A
    ### Question 1
        Your Ansewer
    ### Question 2
        Your Ansewer
    etc.

    Section summaries:
        {combined_summary}

    Here is the metadaata, high level summary as well as the timestamped summary of key points:

    ... Your Reponse ...

    END CONVERSATION.
    """


COMPACT_SUMMARY_QA_PROMPT_TEMPLATE = """
    You are an expert summarizer and question answerer.
    Given the following document, give the metadata of the video such as title and author and
    generate a concise, high-level summary.
    After the summary, generate a list of insightful questions that this document can answer,
    and provide detailed and accurate answers to each.
    There's no need prompt the user to ask questions, as this is a self-contained summary and Q&A.

    RULES:
    1. Format the output as marked down with headers and bullet points.
    2. Give the Youtube metada at the top as a **list**, including: title, author, channel id, url, channel url,
        thumbnail url, language.
    3. Give an overall summary of the transcript.
    4. Breakdown into sections and subsections with bullet points for topics. Each bullet point
        should be a summary of a broad topic instead of an one-liner.
    5. Omit adjacent timestamps that refer to the same broad topic.
    6. Remove any redundancy
    7. Maintain chronological order
    8. Provide a Q&A section at the end with insightful questions and their answers based on the transcript.
    9. Add line breaks immediately after headers and subheaders.

    OUTPUT STRUCTURE:

        # Author: Video Title

        ## Metadata

            - title
            - author
            - channel id
            - url
            - channel url
            - thumbnail url
            - language

        ## Summary

        High level summary. If the transcript is long, make the summary more comprehensive.


        ## Sections

        ### Subsection 1

            - [timestamp 1] Broad topic 1 for Header 1
            - [timestamp 2] Broad topic 2 for Header 1
            - etc.
        ### Subsection 2

            - [timestamp 3] Broad topic 1 for Header 2
            - etc.
        - etc.

        ## Q&A

        ### e.g. What is ...?

            Your Ansewer
        ### e.g. Why does ...?

            Your Ansewer
        etc.


    Document:
        {context_str}

    Here is the metadaata, high level summary as well as the timestamped summary of key points:

    ... Your Reponse ...

    END CONVERSATION.
"""
