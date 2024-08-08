
# Project Setup Instructions

Follow these steps to create a Python virtual environment in the project directory and install all the required packages from the `requirements.txt` file - then run the server.

## Step 1: Create the Virtual Environment

Open a terminal or command prompt and navigate to the project directory. Run the following command to create a virtual environment called `venv`:

```sh
python -m venv venv
```

## Step 2: Activate the Virtual Environment

Activate the virtual environment by running the appropriate command for your operating system:

- On Windows:

```
venv\Scripts\activate
```

- On macOS and Linux:

```
source venv/bin/activate
```

## Step 3: Install the Requirements

With the virtual environment activated, run the following command to install all the packages listed in the `requirements.txt` file:

```
pip install -r requirements.txt
```

This command will read the `requirements.txt` file and install all the listed packages into the virtual environment.

## Step 4: Start the Server

Start the server by running `npm start`. The server will run on localhost:4000