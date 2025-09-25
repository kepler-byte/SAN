<!-- Thank you README Teamplate from: https://github.com/othneildrew/Best-README-Template-->
<a id="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="./app/frontend/public/SAN_White.svg" alt="Logo" width="100" height="100">
  </a>

  <h3 align="center">SAN</h3>

  <p align="center">
    Web application Reading Selling All in one solution
    <br />
    <a href="https://github.com/othneildrew/Best-README-Template">View Demo</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<a href="https://github.com/othneildrew/Best-README-Template">
    <img src="./app/frontend/public/SAN_banner.png" alt="Logo" width="" height="">
  </a>
<br />
<br />

โปรเจ็ค **SAN** สร้างขึ้นเพื่อเป็นโครงงานของ **สถาบันเทคโนโลยีพระจอมเกล้าคุณทหารลาดกระบัง**  คณะครุศาสตร์อุตสาหกรรมและเทคโนโลยี  สาขาเทคโนโลยีคอมพิวเตอร์ วิชา **Principle of Software Design and Development**  

ฟีเจอร์หลักของ Web Application SAN
* Authencation
* Creator Dashboard
* Reading online

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With
[![Svelte](https://img.shields.io/badge/Svelte-%23FF3E00?style=for-the-badge&logo=svelte&logoColor=white)](https://svelte.dev/)  
[![Python](https://img.shields.io/badge/Python-%233776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)  
[![FastAPI](https://img.shields.io/badge/FastAPI-%2300ACC1?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)  
[![MongoDB](https://img.shields.io/badge/MongoDB-%2347A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)  
[![Node.js](https://img.shields.io/badge/Node.js-%23339933?style=for-the-badge&logo=node.js&logoColor=white)](https://nodejs.org/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started


### Prerequisites


* Node.js & npm
* Python 3.10+
* MongoDB running locally or via cloud (Atlas)

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/your-username/san.git
   cd SAN
   ```
2. Install backend dependencies
   ```sh
   cd app/server
   pip install -r requirements.txt
   ```
4. Install frontend dependencies
   ```sh
   cd ../frontend
   npm install
   ```
5. Set environment variables (example .env for backend)
   ```env
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   MONGODB_URI=mongodb://localhost:27017/san
   ```
6. Run backend server
   ```sh
    uvicorn app.main:app --reload
   ```
7. Run frontend 
   ```sh
    npm run dev
   ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

In procewss

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing


### Top contributors:

<a href="https://github.com/kepler-byte/SAN/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=kepler-byte/SAN" alt="contrib.rocks image" />
</a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

```
MIT License

Copyright (c) 2025 Kepler Dev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments
* [Svelte Documentation](https://svelte.dev/)
* [FastAPI Documentation](https://fastapi.tiangolo.com/)
* [MongoDB Documentation](https://www.mongodb.com/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



