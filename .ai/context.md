# Context
This project is about building custom addons for Home Assistant OS version 16. It involves developing endpoints using Python and deploying them inside Docker containers. 

## Subprojects
- `face-rekon` to capture faces and attempt automated recognition.

### Entry Points
- `/face-rekon/ping` - used to verify if the server is online
- `/face-rekon/recognize` - attempts to recognize a face
- `/face-rekon/list` - retrieves a list of all recognized faces

#### Stack
Python, Docker, Flask, NumPy, OpenCV, TinyDB (a lightweight database), Faiss (an efficient similarity search engine).

#### Dependencies
Flask (for setting up the server and defining endpoints), NumPy (for numerical computations), OpenCV (for image processing tasks), TinyDB (as a simple NoSQL database for storing face data), Faiss (to enable fast and accurate face recognition). 

## Best Practices
- **Use Docker**: This ensures consistency across different environments, reducing the risk of discrepancies.
- **Write Unit Tests**: These help ensure that each component of your codebase is working as expected before you integrate it into the main application.
- **Follow SOLID Principles**: Single Responsibility and Open/Closed principles will make your code easier to maintain and extend over time.
- **Use Version Control System (Git)**: Keeping track of changes, collaborating with others, and rolling back to previous versions when necessary are key benefits. 
- **Keep Documentation Updated**: This includes both the code documentation and user guide. It makes it easier for other developers or users to understand what your code does and how they can use it.
- **Monitor Code Quality Metrics**: Tools like SonarQube, CodeClimate etc., help maintain a high standard of coding practices by providing metrics such as code smells, duplicated lines etc.,

Remember that these guidelines are just a starting point. Depending on the complexity of your project and team's expertise in different areas, you might need to devise more specific conventions or best practices.-->
