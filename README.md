# youtube_wrapped
Spotify Wrapped but Youtube

Inspirations: 
- https://github.com/A3M4/YouTube-Report
- https://github.com/Sank6/YouTube-Wrapped

Visualize data from Youtube's watch history obtained from google takeout:
<p float="left"> 
  <img src="https://user-images.githubusercontent.com/103323204/179576059-17056750-4760-486d-82d2-671027d1020b.png" width="300" />          
  <img src="https://user-images.githubusercontent.com/103323204/179576085-51df49d1-0f5a-4408-940f-9c0468224d1e.png" width="300" />        
  <img src="https://user-images.githubusercontent.com/103323204/179576107-a87c5270-efcd-40fb-adb7-5230da042b06.png" width="300" />       
</p>

![image](https://user-images.githubusercontent.com/103323204/179576215-5a5faded-cc40-4a08-a345-51758bcfe9c2.png)


Requires:
- API key with [YouTube Data API v3](https://console.cloud.google.com/marketplace/product/google/youtube.googleapis.com?q=search&referrer=search&project=youtube-347807) enabled
- Youtube *watch-history.json* from [Google Takeout](https://takeout.google.com/settings/takeout)

Future improvements:
- create executable 
- wordcloud for video tags/categories & search history:
  - https://github.com/jasondavies/d3-cloud
  - https://observablehq.com/@contervis/clickable-word-cloud
- matrix chart for hour & dayofweek:
  - https://github.com/kurkle/chartjs-chart-matrix
- better way to parse API response 
- loading screen (and speed up loading time, API calls bottleneck?)
- setup server?
- oauth for project id?
- handle different dates in html file: prob not
