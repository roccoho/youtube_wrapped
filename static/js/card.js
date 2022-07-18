function column(arr, n, col_start, row_start, grid_class_name, col_class_name, link_to=''){
    result = '';
    col_end = col_start + 1;
    for (let i = 0; i < n; i++){
        let links = '';
        if (link_to){
            links = `href=${link_to[i]} target=_blank`;
        }

        result += `<a ${links} class=${grid_class_name}
                      style=grid-column:${col_start};
                            grid-row:${row_start};>
                                ${arr[i]}
                   </a>`;
        row_start = row_start + 2;
    }
    result = `<div class=${col_class_name} style=display:contents;>${result}</div>`;
    return result;
}


function channel(data){
    let grid_class_name = 'channel_list';
    data = data['channel_hist'];

    let number_arr = ['#1', '#2', '#3', '#4', '#5'];
    let links = data['link'];
    let channel_thumbnail = data['thumbnail'];
    let channel_name = data['channelName'];
    let channel_count = data['count'];

    let new_list = '';
    for(let i=0; i<5; i++){
    new_list += `<div class=${grid_class_name}>
                    <div class=channel_number>
                    <a>${number_arr[i]}</a>
                    </div>
                    <div class=channel_thumbnail>
                    <a href=${links[i]} title="${channel_name[i]}" target=_blank l><img src=${channel_thumbnail[i]} class=channel_thumb></a>
                    </div>
                    <div class=channel_name>
                    <a href=${links[i]} title="${channel_name[i]}" target=_blank>${channel_name[i]}</a>
                    </div>
                    <div class=channel_count>
                    <a>Watched ${channel_count[i]} times</a>
                    </div>
                </div>`;
    }
    document.getElementById('channel_top_5').innerHTML = new_list;
}


function video(data){
    let grid_class_name = 'video_list';
    data = data['video_hist'];

    let number_arr = ['#1', '#2', '#3', '#4', '#5'];
    let video_link = data['video_link']; 
    let video_thumbnail = data['thumbnail'];
    let video_name = data['title'];
    let video_count = data['count'];
    let video_chan_name = data['channelName'];
    let video_chan_link = data['chan_link'];

    let new_list = '';
    for(let i=0; i<5; i++){
    new_list += `<div class=${grid_class_name}>
                    <div class=video_number>
                    <a >${number_arr[i]}</p>
                    </div>
                    <div class=video_thumbnail>
                    <a href=${video_link[i]} title="${video_name[i]}" target=_blank><img src=${video_thumbnail[i]} class=video_thumb></a>
                    </div>
                    <div class=video_name>  
                    <a href=${video_link[i]} title="${video_name[i]}" target=_blank>${video_name[i]}</a>
                    </div>
                    <div class=video_chan_name>
                    <a href=${video_chan_link[i]} title="${video_chan_name[i]}" target=_blank>${video_chan_name[i]}</a>
                    </div>
                    <div class=video_count>
                    <a>Watched ${video_count[i]} times</a>
                    </div>
                </div>`;
    }
    document.getElementById('video_top_5').innerHTML = new_list;
}


function summary(data){
    document.getElementById("summary_minutes_watched").innerHTML = data["stats"]["value"][1];
    document.getElementById("summary_videos_watched").innerHTML = data["stats"]["value"][0];
    document.getElementById("summary_optimal_length").innerHTML = data["stats"]["value"][3];

    grid_class_name = 'top_5_grid';
    top_numbers = 5;
    let number_arr = ['#1', '#2', '#3', '#4', '#5'];
    let numbering1 = column(number_arr, top_numbers, 1, 1, grid_class_name, 'summary_number');
    let numbering2 = column(number_arr, top_numbers, 4, 1, grid_class_name, 'summary_number');

    let videos = data["video_hist"]["title"];
    let video_link = data["video_hist"]["video_link"];
    let new_video_list = column(videos, top_numbers, 2, 1, grid_class_name, 'summary_video_list', video_link);

    let channels = data["channel_hist"]["channelName"];
    let channel_link = data["channel_hist"]["link"];
    let new_channel_list = column(channels, top_numbers, 5, 1, grid_class_name, 'summary_channel_list', channel_link);

    let new_list = numbering1 + new_video_list + numbering2 + new_channel_list;
    document.getElementById("summary_top_5_lists").innerHTML = new_list;
}


function paging(ele_id) {
    let current_div = document.getElementById(sum_div_arr[sum_active_div]);
    current_div.style.display = "none";
    if (ele_id == "left_arrow")
        sum_active_div -= 1;
    else if (ele_id == "right_arrow")
        sum_active_div += 1;
    new_div = document.getElementById(sum_div_arr[sum_active_div]);
    new_div.style.display = "block";
    active_arrow();
}


function active_arrow(){
    if (sum_active_div == 0){
        left_arrow.style.display = "none";
        right_arrow.style.display = "block";
    }else if (sum_active_div == sum_div_arr.length-1){
        left_arrow.style.display = "block";
        right_arrow.style.display = "none";
    }else{
        left_arrow.style.display = "block";
        right_arrow.style.display = "block";
    }
}

function tag(data){
    data = data['tags_hist'];
    var chart_data = [];
    for(let i=0; i < data['tag'].length; i++){
        chart_data.push({x: data['tag'][i], value: data['count'][i]});
    }
    console.log(chart_data);
    var any_chart = anychart.tagCloud(chart_data);  
    any_chart.container("tag_top_5");
    any_chart.draw();
}
