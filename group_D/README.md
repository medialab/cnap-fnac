
# requierements

- python 2.7
- node.js
- pip install -r requirements.txt
- a mongodatabase
- FNAC data downloaded and inserted into mongo thanks to :
	- download_all_data.sh
	- dataToMongo.js

# artist_frequency.py
Use the mongodatabase to compute the **artists_frequency.json** file.  
This file creates a profile by artist in which all the dates related to his artworks bought by the fnac are summarized :

```json
 {
        "author_ids": [
            "140000000003716"
        ], 
        "dates_weighted": {
            "1868": 1, 
            "1869": 1, 
            "1870": 1, 
            "1876": 1, 
            "1880": 1, 
            "1881": 2
        }, 
        "name": "Just LHERNAULT", 
        "transfert_dates": [
            1880
        ], 
        "deposit_dates": [
            1869, 
            1881
        ], 
        "exhibition_dates": [], 
        "creation_years": [
            1868, 
            1881
        ], 
        "acquisition_years": [
            1870, 
            1876, 
            1868, 
            1881
        ]
    }
 ``` 

# artist_frequency_vector.py

This script post-treats the **artists_frequency.json** to compute the date sequences of artits' profiles which inclused 0 to missing years.  
It outputs **artists_profils_sequences.json**:

```json
    {
        "author_ids": [
            "140000000003716"
        ], 
        "dates_weighted": {
            "1876": 1, 
            "1870": 1, 
            "1869": 1, 
            "1868": 1, 
            "1881": 2, 
            "1880": 1
        }, 
        "name": "Just LHERNAULT", 
        "first_date": 1868, 
        "event_sequence_with_0": [1,1,1,0,0,0,0,0,1,0,0,0,1,2], 
        "event_sequence_without_0": [1,1,1,1,1,2]
    }
```

# artworks_sequences_relationalEsthesism.py

This script uses **artists_name_esthetic_relational.txt** list of artist name which were extracted from the book "l'Esthétique Relationnelle (1985-2001)" from Nicolas Bourriaud (2011).  
This script uses the same principles than artist_frequency.py.  
It outputs **er_artworks_frequency.json** which list artworks dates (creation, acquisition, exhibitions, deposit, transfert) of the Esthétique Relationnelle book.  

```json
{
        "acquisition_year": 1990, 
        "transfert_dates": [
            2008
        ], 
        "title": "Caisson lumineux", 
        "creation_year": 1989, 
        "exhibition_dates": [
            1988, 
            1989
        ], 
        "dates_weighted": {
            "2008": 1, 
            "1988": 1, 
            "1989": 2, 
            "1990": 1
        }, 
        "deposit_dates": [], 
        "author(s)": "CERCLE RAMO NASH"
 } 
```

This file is used by the artists-work-ER/index.html web app to be visualized.

# timeseries_clustering

This submodule uses the [Triangular Global Alignment Kernels](http://www.iip.ist.i.kyoto-u.ac.jp/member/cuturi/GA.html) method to compute a similarity measure between artists' time profils.

## TGA_python_wrapper

This submodule adds **numpy** and **cython** to the requierments.  
One needs to follow [TGA_python_wrapper/README](TGA_python_wrapper/README) instructions to compile the python wrapper.

## artists_sequences_TGA_similarities.py

This script computes a TGA similarity measure between artists' sequences.  
It can be configured to filter the 20000s artists profile to a narrower set.  
Available filters :
```python
artists_random_select_percentage=None
event_sequence_length_min=190
er_authors_filtered=None
```

- Reduce the list of artists' sequences to a random set of *artists_random_select_percentage* percentage
- Reduce the list of artists' sequences to those whose length maximises *event_sequence_length_min*
- Reduce the list of artists' sequences to artists being part of or coauthors with the Relational Aesthetism movement

