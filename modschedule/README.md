# Modschedule
Automatically finds a random clash-free timetable given module selections.

## Features

- Clash finding algorithm uses interval tree for $O(log(n))$ clash lookup.
- Web scraper automatically fetches module information from NTU class schedule website.


## Install
```sh
npm install
```

## Usage
Find a random timetable for module codes:
```sh
npx ts-node index.ts CC0007 SC2000 SC2001 SC2005 SC2006 SC2207
```


See usage information:
```sh
npx ts-node index.ts -h
```

## Tests
Run unit tests
```sh
npm test
```
