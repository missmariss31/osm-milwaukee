# Benefits and Issues

While investigating the OSM dataset, I found some potential improvements.

1.  Abbreviated street types can be changed to full street type name (Ave: Avenue, etc)
    -  Benefits:
        1.  All street types will be identified and searchable by standards
        2.  The data will look clean and conformed to standards
        3.  Types will be clearly stated with little chance for misinterpretation
      
    -  Anticipated Issues:
        1.  Not all street types will be recognizable programmatically
        2.  There is the potential for street name to be mistaken for street type and corrected in error
        3.  Anyone searching the database using abbreviated street types may be unable to complete a successful search
       <br> 
       <br>
2.  Abbreviated street directions can be changed to full street direction name (N: North, etc.)
    -  Benefits:
        1.  All street directions will be identified and searchable by standards
        2.  The data will look clean and conformed to standards
        3.  Directions will be clearly stated with little chance for misinterpretation
      
    -  Anticipated Issues:
        1.  If all "N", "S", "E", and "W" characters are changed to directions, there may be some changed in error (Highway E, County Road W)
        2.  Any direction not abbreviated according to standards will be missed
        3.  Anyone searching the database using abbreviated street types may be unable to complete a successful search
        <br>
        <br>
3.  Postcodes can be checked for conformity (5-digit codes) and against Milwaukee area codes <-- Same with "county" (Milwaukee, WI)
    -  Benefits:
        1.  All postcodes will be identified and searchable by standards
        2.  The data will look clean and conformed to standards
        3.  Postcodes will be clearly stated with little chance for misinterpretation
    
    -  Anticipated Issues:
        1.  If non Milwaukee postal code tags are taken out, other information may need to be taken out as well (street names, etc.)
        2.  Some non Milwaukee area codes and corresponding information may be listed as a reference to important landmarks surrounding Milwaukee or for navigation purposes.  We may not want this taken out of our database. 
        3.  Some postcodes utilize a ZIP+4 system and cutting postcodes down to 5-digits may put any postal service utilizing OSM at a disadvantage.  
        <br>
        <br>
4.  Phone numbers can be checked for conformity (+1-555-555-5555) and Milwaukee area code (414)
    -  Benefits:
        1.  All phone numbers may be used for autodialing applications with ease
        2.  The data will look clean and conformed to standards
        3.  Phone numbers will be clearly stated with little chance for misinterpretation
        
    -  Anticipated Issues:
        1.  Numbers without Milwaukee area codes may be cell phone numbers or businesses with multiple locations, so we may not want to take those numbers out of the database.
        2.  There may be errors when dealing with numbers less than 10 digits, as it may be difficult to determine area code
        3.  Those that are unfamiliar with the chosen format may be unable to search the database using phone numbers
        <br>
        <br>
5.  Web Addresses may be checked for validity and conformity (https?.\..)
    -  Benefits:
        1.  All websites will be identified and searchable by standards
        2.  The data will look clean and conformed to standards
        3.  Websites will be clearly stated with little chance for misinterpretation
        
    -  Anticipated Issues:
        1.  It may be unclear as to whether a website uses http or https if not specified
        2.  If we exclude websites that do not conform to standards we have set, there may be a loss of significant information
        3.  Those that are unfamiliar with the chosen format may not be able to search using websites
        <br>
        <br>

## Conclusion

In conclusion, we have investigated our sample and made a few improvements.  After creating our SQL database, we've performed a few queries to record data statistics and discover additional potential improvements to our dataset.  We have also discovered a few interesting bits of information about Milwaukee, such as the fact that there is one area with access for horse riders!  
      