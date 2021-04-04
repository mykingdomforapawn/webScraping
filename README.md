# webScraping
> This was one of the first projects I implemented. Therefore, it is far from perfect. 
> If you have any suggestions concerning the programming style, implementation, documentation, etc. please let me know.

## Table of contents:
- [What is it?](#what-is-it)
- [Why did I do it?](#why-did-i-do-it)
- [How to use it?](#how-to-use-it)
- [Would I do it again?](#would-i-do-it-again)

---

## What is it?
This is a web scraper designed to accumulate geographical, financial and social data about all sovereign countries from Wikipedia. This process follows two steps. First, a list of all countries and the links to their Wikipedia page is downloaded. Second, each Wikipedia page is visited individually (see left picture) to scrape previously defined features of a country. The data is used to create a geography quiz based on Anki flashcards (see right picture).

![Screenshot website](https://github.com/mykingdomforapawn/webScraping/blob/main/media/screenshot_website.JPG)
![Screenshot flashcard](https://github.com/mykingdomforapawn/webScraping/blob/main/media/screenshot_flashcard.JPG)

## Why did I do it?
**The big picture:** To have an idea abouts what's going on in the world, it is absolutely necessary to know and compare geographical, financial and social facts about countries. Many conflicts, political movements and social changes can be explained with these numbers and maps.

**Information literacy:** I tried a few geography apps but the data was incomplete or too detailed. This project allows me to decide which information to learn.

**Programming skills:** Learning and applying programming skills was a part of my studies, but writing a few lines for an assignment with a predefined result and conceptualising/implementing a whole project by yourself are two completly different things.


## How to use it?
1. Getting started: Set up a [virtual environment](https://docs.python.org/3/library/venv.html) and [install the modules](https://pip.pypa.io/en/stable/user_guide/) from *requirements.txt*.
3. Defining the features: Add or remove features in the *feature_list.csv* file.
5. Running the script: Run *geography_data_scraper.py*.
4: The data: The accumulated data will be stored in *data.csv* (semicolon seperated), each row beeing a country and each column a feature.
5. From data to flashcards: You can either create your own anki flashcard templates and import the *data.csv* or you can directly import the cards I created to your anki app. In the latter case, you obviously don't have to run the script etc.

## Would I do it again?
Big yes! Not only did I learn a lot more from implementing this idea compared to an assigned task, but also the stisfaction of finishing a personal project is worth it.
