# sampley: sample survey data

## Description
The ```sampley``` package serves to sample survey data (hence 'sampley': 'sample' + 'survey'). By 'survey data', we refer 
principally to systematic visual survey data, nevertheless, the ```sampley``` package may also be applicable to other 
kinds of survey data. By 'sample', we mean process those data to produce distinct samples that can then be input to a 
model.
<br><br>Data can be processed by one or more of three approaches referred to here as the grid, segment, and point approach.
<br>The **grid approach** consists of overlaying a grid, typically rectangular or hexagonal, onto the study area and 
allocating detections and, optionally, survey effort to the cells that they lie within. Additionally, data may be 
allocated to temporal periods. Each cell within a given period then serves as a sample.
<br>The **segment approach** involves taking sections of continuous, uniform survey effort and cutting them into segments
of standardised lengths which serve as samples.
<br>The **point approach** consists of using the detections, or a subset thereof, as presences and then sampling absences
from absence zones (i.e., areas that were surveyed but where the species was not detected).
<br><br>For more information, please consult the User Manual (available on the GitHub repo at: 
https://github.com/JSBigelow/sampley/blob/main/sampley%20-%20User%20Manual.pdf).

## Installation
```pip install sampley```

## Import
For basic utilisation of ```sampley```, run:
<br>```from sampley import *```

To access the underlying functions, run:
<br>```from sampley.functions import *```

## User Manual
A user manual containing more detailed information is available on GitHub at:
https://github.com/JSBigelow/sampley/blob/main/sampley%20-%20User%20Manual.pdf

## Example usage
Several exemplars illustrating how to use ```sampley``` are available on GitHub at: 
https://github.com/JSBigelow/sampley/tree/main/exemplars

See the _Introduction to sampley exemplars_ (```intro.ipynb```) for more information 
(https://github.com/JSBigelow/sampley/blob/main/exemplars/intro.ipynb)

## License
MIT
