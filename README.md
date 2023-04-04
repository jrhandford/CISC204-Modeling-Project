# CISC/CMPE 204 Modelling Project

In this project, we model the river crossing puzzle in bauhaus, a python library for encoding and solving things using propositional logic.

In the river crossing puzzle, a farmer starts on one side of a river alongside a cabbage, goat, and wolf. He has a boat which can only carry him and one other thing across the river. However, if he leaves the goat alone with the wolf, the wolf will eat the goat, and if he leaves the goat alone with the cabbage, the goat will eat the cabbage.  The farmer needs to figure out the sequence of steps he needs to take in order to take everyone across the river intact.

The program in this project is pre-configured to solve the river crossing puzzle in the least amount of moves, but its variables can be adjusted to change the number of moves allowed, along with increasing/decreasing the number of animals and which animals can't be left alone without the farmer. 

## Structure
* `run.py`: Main program file. Run this in docker using the command 'python3 run.py'

## Running With Docker

By far the most reliable way to get things running is with [Docker](https://www.docker.com).

1. First, download Docker https://www.docker.com/get-started and the project as a zip. Unzip the project into a folder.

2. Navigate to the root of the project folder on the command line.

3. We first have to build the course image. To do so use the command:
`docker build -t cisc204 .`

4. Now that we have the image we can run the image as a container by using the command: `docker run -it -v $(pwd):/PROJECT cisc204 /bin/bash`

    `$(pwd)` will be the current path to the folder and will link to the container

    `/PROJECT` is the folder in the container that will be tied to your local directory

5. To run the program in Docker, type 'python3 run.py' in the Docker terminal with the container running. If it's working correctly, you should see an output in the console.

6. To play around with the results, you may modify the variables at the top of the main function in run.py.

### Mac Users w/ M1 Chips

If you happen to be building and running things on a Mac with an M1 chip, then you will likely need to add the following parameter to both the build and run scripts:

```
--platform linux/x86_64
```

For example, the build command would become:

```
docker build --platform linux/x86_64 -t cisc204 .
```

### Mount on Different OS'

In the run script above, the `-v $(pwd):/PROJECT` is used to mount the current directory to the container. If you are using a different OS, you may need to change this to the following:

- Windows PowerShell: `-v ${PWD}:/PROJECT`
- Windows CMD: `-v %cd%:/PROJECT`
- Mac: `-v $(pwd):/PROJECT`

Finally, if you are in a folder with a bunch of spaces in the absolute path, then it will break things unless you "quote" the current directory like this (e.g., on Windows CMD):

```
docker run -it -v "%cd%":/PROJECT cisc204
```
