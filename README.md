## PunGenT: Pun Generation Toolchain
##### Lance Choong, Eren Kahriman, Thai Truong, and Jason Wan

Welcome to PunGenT, a project aimed at offering a list of puns based on a user's input. The project is being developed by Lance Choong, Eren Kahriman, Thai Truong, and Jason Wan as part of CSDS 395.


**Background and Vision Statement**

Puns are a common type of wordplay that serve as a source of humor in everyday language. Despite their significance, automated pun generation has received relatively little research. The majority of the resources for pun creation currently available are either lists of already existing puns or rule-based systems with limited functionality. Although AI language models such as ChatGPT are growing in popularity, they are too computationally expensive to run locally and may not provide sufficient availability.

In light of these shortcomings, the purpose of this research project is to create a tool that can produce puns instantly from a user's few input words as a brainstorming tool. Through the use of a carefully curated database of puns, the system will be created to produce puns that are both appropriate and humorous. The objective is to provide a user-friendly interface that enables users to quickly generate puns for a variety of purposes, including improving their language skills, creating amusing content, or honing their conversational pun-making abilities. The results of this study can be put to use in the fields of conversational agents, entertainment, and language learning.

**Scope**

The PunGenT project is expected to produce a user-friendly tool that can generate puns based on user input. The tool will use a carefully curated database of puns and implement state-of-the-art natural language processing techniques to create appropriate and humorous puns. The tool will have a command-line interface that will accept input from users, and output the generated puns.

## Usage
Each component's subdirectory contains a `README` detailing usage of each module.
To use with the React frontend, `cd` into the `flask-server` directory and `python -m flask --app ./server.py run`.
Then follow the instructions in the frontend `README` to open the client.

## Dependencies
The cumulative used Python packages beyond the standard library are listed in `requirements.txt`. However, not all of these packages are necessary for all of the components. Each component's subdirectory contains a `README.md` with a table that displays the dependencies per module.
