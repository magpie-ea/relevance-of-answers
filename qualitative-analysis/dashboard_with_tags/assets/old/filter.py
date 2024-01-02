## HELPER FUNCTIONS
# def get_rowlabel(id):
def apply_filter(button_n_clicks, condition_col_1, condition_stat_1, comparison_op, condition_col_2, condition_stat_2):
    # check if filter is valid
    valid_filter_condition = all([
        condition_col_1, condition_stat_1, comparison_op, condition_col_2, condition_stat_2])
    # On click, apply or remove filter (if valid)
    if button_n_clicks % 2 == 1:
        if valid_filter_condition:  
            filter_flag = 'on'
            query_str = f'{condition_col_1}_{condition_stat_1} {comparison_op} {condition_col_2}_{condition_stat_2}'
        else:
            filter_flag = 'invalid'
            query_str = None
    else:
        filter_flag = 'off'
        query_str = None
    return query_str, filter_flag

def update_button_style(filter_flag):
    if filter_flag == 'on':
        button_style = styles.blue_button_style
        button_text = 'Filter Applied'
    elif filter_flag == 'off':
        button_style = styles.white_button_style
        button_text = 'Apply Filter'
    elif filter_flag == 'invalid':
        button_style = styles.red_button_style
        button_text = 'Invalid Filter'
    return button_style, button_text

@dash.callback(
    Output('filter-settings', 'data'),
    Output('filter-button', 'style'),
    Output('filter-button', 'children'),
    [
        Input('condition-col-1', 'value'),
        Input('condition-stat-1', 'value'),
        Input('comparison-op', 'value'),
        Input('condition-col-2', 'value'),
        Input('condition-stat-2', 'value'),
        Input('filter-button', 'n_clicks'),
    ],
)
def update_filter_settings(condition_col_1, condition_stat_1, comparison_op, 
                 condition_col_2, condition_stat_2, button_n_clicks):
    query_str, filter_flag = apply_filter(button_n_clicks, 
                    condition_col_1, condition_stat_1, comparison_op, condition_col_2, condition_stat_2)
    button_style, button_text = update_button_style(filter_flag)
    filter_settings = {}
    filter_settings['flag'] = filter_flag
    filter_settings['query'] = query_str
    return filter_settings, button_style, button_text