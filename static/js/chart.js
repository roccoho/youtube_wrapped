
function createData(x_axis, y_axis, y_id, y_label, color){
    let data_ = {labels: x_axis};
    data_['datasets'] = [];
    for (let i = 0; i < y_axis.length; i++){
        data_['datasets'].push({barPercentage: 1.0,
                                categoryPercentage: 0.8,
                                label: y_label[i],
                                yAxisID: y_id[i],
                                backgroundColor: color[i],
                                data: y_axis[i],
                                borderWidth: 1,
                                borderColor: '#777',
                                hoverBorderWidth: 3,
                                hoverBorderColor: gray
                                })
    };
    return data_;
}


function createScale(y_id, graph_name){
    let scales = {};
    if (graph_name == 'day_hist'){
        scales['x'] = {type: 'time',
                           time: {
                              parser: 'YYYY-MM-DD',
                              unit: 'month',
                              displayFormats: {
                                  month: 'MMM'
                                  },
                              tooltipFormat: 'DD-MMM-YYYY'
                                },
                            grid: {display: true,
                                    color: gray
                                 }
                            };
    }else{
        scales['x'] = {grid: {display: false,
                              color: gray
                                }
                        };
    }


    scales[y_id[0]] = {type: 'linear',
                           position: 'left',
                           grid: {
                                display: true,
                                color: gray
                           }};

    if(y_id.length > 1){
        scales[y_id[1]] = {type: 'linear',
                               position: 'right',
                               grid: {
                                    display: false,
                                    color: gray
                               }};
    }
    return scales;
}


function createOption(graph_data, graph_type, graph_title, scale){
    let chart_option = {
        type: graph_type,
        data: graph_data,
        options: {
            barValueSpacings: 0,
            responsive: true,
            scales: scale,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: graph_title,
                    align: 'start',
                    font: {
                        size: 25,
                    }
                },
                legend: {
                    display: true,
                    position: 'top',
                    align: 'end',
                    labels: {
                        color: white
                    }
                },
                tooltip: {
                    enabled: true // Default
                }
            },
            layout: {
                padding: {
                    left: 0,
                    right: 200,
                    bottom: 0,
                    top: 0
                }
            },
        }
    };

    return chart_option;
}

function destroyChart(){
    ['normal_chart', "day_chart"].forEach(function(cur_chart){ 
        let chartStatus = Chart.getChart(cur_chart); // <canvas> id
        if (chartStatus != undefined) {
            chartStatus.destroy();
        }
    }); 
}

function updateColor(other_radios, current_button){
        for(let i = 0; i < other_radios.length; i++){
            other_radio = document.getElementById(other_radios[i]);
            closest_div = other_radio.closest('div');
            closest_div.style.backgroundColor = transparent; 
            // closest_div.onmouseover = mouseOver(closest_div.id);  
            // closest_div.onmouseout = mouseOut(closest_div.id);  
        }   
        target_div = document.getElementById(current_button); 
        closest_target = target_div.closest('div');
        closest_target.style.backgroundColor = 'rgb(56, 56, 56)';  
        // closest_target.onmouseover = null;  
        // closest_target.onmouseout = null;  
}


function updateAnchor(anchor_id){
    if(!anchor_id){
        anchor_id = 'summary_anc';
    }

    for(let i = 0; i < anchor_divs.length; i++){
        current_anc = document.getElementById(anchor_divs[i]);
        current_anc.style.backgroundColor = transparent;
    }

    target_anc = document.getElementById(anchor_id);
    target_anc.style.backgroundColor = 'rgb(56, 56, 56)';
} 


// function mouseOver(div_id) {  
//     console.log('in');
//     document.getElementById(div_id).style.backgroundColor = 'rgb(56, 56, 56)';
// }
// function mouseOut(div_id) { 
//     console.log('out');
//     document.getElementById(div_id).style.backgroundColor = transparent;
// }

function goToAnchor(anchor) {
    var loc = document.location.toString().split('#')[0];
    document.location = loc + '#' + anchor;
    return false;
  }


function chooseGraph(radio_id){  
    destroyChart();  

    if(!radio_id){  //default selection
        goToAnchor('chart_div');
        radio_id_y = 'both_radio';
        radio_id_chart = 'line_chart';
        radio_id_graph = 'graph_year';
        updateColor(chart_type_divs, radio_id_chart);
        updateColor(graph_type_divs, radio_id_graph);
        updateColor(y_axis_type_divs, radio_id_y);
    }else{
        goToAnchor('graph_div');
        if (chart_type_divs.includes(radio_id)){
            updateColor(chart_type_divs, radio_id);
        }else if(y_axis_type_divs.includes(radio_id)){
            updateColor(y_axis_type_divs, radio_id);
        }else if(graph_type_divs.includes(radio_id)){
            updateColor(graph_type_divs, radio_id);
        }
    }
    let chart_type = document.querySelector('input[name="chart_type"]:checked').value;
    let y_axis_type = document.querySelector('input[name="y_axis_type"]:checked').value;
    let selected_chart = document.querySelector('input[name="graph_type"]:checked').value; 
    let data_ = data[selected_chart];
 
    if(y_axis_type == 'video'){
        y_id = ['videocount'];
        graph_data = createData(data_['x_axis'], [data_['count']], y_id, ['Videos'], [main_color]);
    }else if(y_axis_type == 'watch'){
        y_id = ['watchtime'];
        graph_data = createData(data_['x_axis'], [data_['duration']], y_id, ['Watch time (minutes)'], [sec_color]);
    }else{
        y_id = ['videocount', 'watchtime'];
        graph_data = createData(data_['x_axis'],
                                [data_['count'], data_['duration']],
                                y_id,
                                ['Videos', 'Watch time(minutes)'],
                                [main_color, sec_color]);
    }

    let graph_title = '';
    if (selected_chart == 'day_hist'){
        graph_title = 'Daily Analytics';
        var myChart = document.getElementById("day_chart").getContext('2d');
        scroll_chart_div.style.display = "block"; 
        normal_chart_div.style.display = "none";
    } 
    else{
        var myChart = document.getElementById("normal_chart").getContext('2d');
        scroll_chart_div.style.display = "none"; 
        normal_chart_div.style.display = "block";
        if (selected_chart == 'hour_hist'){
            graph_title = 'Hourly Analytics';
        }
        else if (selected_chart == 'week_hist'){
            graph_title = 'Weekly Analytics';
        }
        else if (selected_chart == 'month_hist'){
            graph_title = 'Monthly Analytics';
        } 
        else if (selected_chart == 'week_hour_hist'){
            graph_title = 'Week/Hour Analytics';
        }
    }

    if(selected_chart == 'week_hour_hist'){   
        if(y_axis_type == 'watch'){
            values = data_['duration'];
            values = values.map(v=> v + ' minutes'); 
            color = data_["duration_color"];
            border_color = 'rgba(64, 181, 217, 1)';
        }else{ 
            values = data_['count'];
            values = values.map(v=> 'count: ' + v); 
            color = data_["video_color"];
            border_color = "rgba(189, 105, 242, 1)";
        } 
        
        var new_data = []; 
  
        for(let i=0; i < data_['day'].length; i++){
            new_data.push({x: data_['x_axis'][i], 
                           y: data_['day_short'][i], 
                           value: values[i], 
                           long_day: data_['day'][i]});
        }
        
        var chart = new Chart(myChart, {
            type: 'matrix',
            data: {
              datasets: [{ 
                data: new_data,
                backgroundColor: color, 
                borderColor: border_color,
                borderWidth: 1,
                width: ({chart}) => (chart.chartArea || {}).width / 24 - 1,
                height: ({chart}) =>(chart.chartArea || {}).height / 7 - 1
              }]
            }, 
            options: {
              layout: {
                padding: { 
                    top: 100,
                    right: 200
                    }
                },  
              maintainAspectRatio: false,
              responsive: true, 
              plugins:{ 
                title: {
                    display: true,
                    text: graph_title,
                    align: 'start',
                    font: {
                        size: 25,
                    }
                },
                legend: {
                    display: false, //set to false
                    position: 'top',
                    align: 'end',
                    title: {
                        text: 'Videos' //not working
                    },
                    labels: {
                        color: white
                    }
                },
                tooltip: {
                    callbacks: {
                        label(context){
                            const v = context.dataset.data[context.dataIndex];    
                            return ['x: ' + v['x'], 'y: ' + v['long_day'], v['value']];
                        }
                    }
                } 
              },
              scales: {
                x: {
                  type: 'category',
                  labels: get_label(data_['x_axis']),
                  display: true,   
                  offset: true,     
                  grid: {
                      display: false
                  }
                },
                y: {
                  labels: get_label(data_['day_short']),
                  type: 'category',
                  display: true, 
                  offset: true,        
                  grid: {
                      display: false
                  }
                }
              }
            }
          });

    }
    else{
        let chart_scale = createScale(y_id, selected_chart);
        var chart = new Chart(myChart, createOption(graph_data, chart_type, graph_title, chart_scale));
    }
}


function get_label(axis_label){ 
    return [... new Set(axis_label)]
  }

