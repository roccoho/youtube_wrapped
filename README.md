# Youtube Wrapped  

**Working link:**  
https://youtubewrap.herokuapp.com/  
(please be patient because it is ran on a free tier Heroku server TT)

**Inspirations:** 
- https://github.com/A3M4/YouTube-Report
- https://github.com/Sank6/YouTube-Wrapped


**Visualize data from Youtube's watch history obtained from google takeout**:
<p float="left"> 
  <img src="https://user-images.githubusercontent.com/103323204/179581096-e8004bff-747e-4835-a2ac-791c6f6b0fb1.png" width="250" />          
  <img src="https://user-images.githubusercontent.com/103323204/179581176-2a650585-ea9d-48a9-b7c6-77b9f409bb54.png" width="250" />        
  <img src="https://user-images.githubusercontent.com/103323204/179581232-66e4f9af-9aea-4a99-97e4-300241da9973.png" width="250" />       
</p>  

<img src="https://user-images.githubusercontent.com/103323204/179576215-5a5faded-cc40-4a08-a345-51758bcfe9c2.png" width="750" /> 



**Requires:**
- API key with [YouTube Data API v3](https://console.cloud.google.com/marketplace/product/google/youtube.googleapis.com?q=search&referrer=search&project=youtube-347807) enabled
- Youtube *watch-history.json* from [Google Takeout](https://takeout.google.com/settings/takeout)


**Future improvements:**
- top categories
- locked y-axis graph horizontal scrolling
- better way to parse API response 
- speed up loading time, API calls bottleneck? 
- oauth for api key?
- handle different dates in html file: probably not
- what happens if there are concurrent users? no idea
