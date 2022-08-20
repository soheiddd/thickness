import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import streamlit as st
import numpy as np
import codecs



st.markdown("## Wall Thickness Research")

# Layout (Sidebar)
uploaded_file = st.file_uploader("File Upload", type="csv")

st.write("-----------------------------------------------------------------------------------------------------------------")

vars_thickness = ["Number of 1pcs" , "Number of 2pcs" , "Number of 3pcs" , "Number of 4pcs"]
###st.markdown("## Settings")
st.sidebar.markdown("## Target Variables")
nikuatu_selected = st.sidebar.selectbox('Categorical Variables', vars_thickness)

ucl_side=st.sidebar.number_input('UCL:',step=0.1)
lcl_side=st.sidebar.number_input('LCL:',step=0.1)


def main():

    if uploaded_file is not None:
        #列名～取り個数取得
        col_names = [ 'c{0:02d}'.format(i) for i in range(35) ]
        df = pd.read_csv( uploaded_file , sep=',' , names = col_names ,encoding="utf-8")
        
        ###Data Table作成
        number_of_pieces_str = df["c00"][3]
        number_of_pieces_int = int(number_of_pieces_str)

        #測定情報解析
        df_measure_amount = int(df.iloc[4]["c00"])
        #df_measure_amount_last_line = int((df_measure_amount / number_of_pieces_int ) + 5)
        df_measure_amount_last_line = int(df_measure_amount)
        measure_amount_for_hist = int(df_measure_amount / 3)
    
        #取り個数別条件
        df_product_data = df[5:df_measure_amount_last_line]
        df_product_data.reset_index(drop=True,inplace=True)
        
        #計画NO
        plan_no = df["c00"][5]

        #品番
        products_no = df["c01"][5]

    if uploaded_file is not None:
        if number_of_pieces_int == 1:
            df_N_product_data = df_product_data[["c03","c04"]]
            df_N_product_data_rename = df_N_product_data.rename(columns = {"c03":"1-T1","c04":"1-T2"})
        
        elif number_of_pieces_int == 2:            
            #データ処理
            df_N_product_data = df_product_data[["c02","c03","c04","c05","c06"]]
            df_N_product_data_rename = df_N_product_data.rename(columns = {"c02":"Mea_hist","c03":"1-T1","c04":"1-T2","c05":"2-T1","c06":"2-T2"})
            df_N_product_data_allint = df_N_product_data_rename.astype({"1-T1":float})
            #df_N_product_data_allint = df_N_product_data_rename.fillna(9999)
            df_N_product_data_allint["thickness_1"] = np.where(df_N_product_data_allint['1-T1']>df_N_product_data_allint['1-T2'],df_N_product_data_allint['1-T1'], df_N_product_data_allint['1-T2'])
            df_N_product_data_allint["thickness_2"] = np.where(df_N_product_data_allint['2-T1']>df_N_product_data_allint['2-T2'],df_N_product_data_allint['2-T1'], df_N_product_data_allint['2-T2'])
            df_N_product_data_allint["USL"] = ucl_side
            df_N_product_data_allint["LSL"] = lcl_side
            df_thickness_1 = df_N_product_data_allint.loc[:,["thickness_1"]]
            df_thickness_2 = df_N_product_data_allint.loc[:,["thickness_2"]]

            #全データ
            df_show_data = df_N_product_data_allint[["thickness_1","thickness_2","Mea_hist"]]
            df_show_data.fillna({"Mea_hist": 0},inplace=True)

            #工程能力計算(Base)
            df_within_tolerance_1 = df_thickness_1.query("@lcl_side < thickness_1 < @ucl_side")
            df_within_tolerance_2 = df_thickness_2.query("@lcl_side < thickness_2 < @ucl_side")
            df_describe_1 = df_within_tolerance_1.describe()
            df_describe_2 = df_within_tolerance_2.describe()
            df_describe_all = pd.concat([df_describe_1,df_describe_2],axis=1)
            
            #工程能力計算(標準偏差)
            std_1 = df_describe_all.at['std', 'thickness_1']
            std_2 = df_describe_all.at['std', 'thickness_2']                       
            std6_1 = std_1*6
            std6_2 = std_2*6
            
            #工程能力計算(Cp)
            tolerance_width = ucl_side - lcl_side
            cp_1 = tolerance_width / std6_1
            cp_2 = tolerance_width / std6_2
            cp_dataframe = pd.DataFrame({"thickness_1":[cp_1],"thickness_2":[cp_2]})
            cp_dataframe.index = ["Cp"]
            
            #工程能力計算(Cpk)
            avg_1 = df_describe_all.at['mean', 'thickness_1']
            avg_2 = df_describe_all.at['mean', 'thickness_2']
            k1 = abs((ucl_side + lcl_side)/2 - avg_1) / (ucl_side + lcl_side)/2
            k2 = abs((ucl_side + lcl_side)/2 - avg_2) / (ucl_side + lcl_side)/2
            cpk_1 = (1-k1)*cp_1
            cpk_2 = (1-k2)*cp_2
            
            cp_dataframe = pd.DataFrame({"thickness_1":[cp_1,cpk_1],"thickness_2":[cp_2,cpk_2]})
            cp_dataframe.index = ["Cp","Cpk"]
            df_add_cp = pd.concat([df_describe_all, cp_dataframe])

            
        elif number_of_pieces_int == 3:
            #データ処理
            df_N_product_data = df_product_data[["c02","c03","c04","c05","c06","c07","c08"]]
            df_N_product_data_rename = df_N_product_data.rename(columns = {"c02":"Mea_hist","c03":"1-T1","c04":"1-T2","c05":"2-T1","c06":"2-T2","c07":"3-T1","c08":"3-T2"})
            df_N_product_data_allint = df_N_product_data_rename.astype({"1-T1":float})
            df_N_product_data = df_product_data[["c02","c03","c04","c05","c06","c07","c08","c09","c10"]]
            df_N_product_data_rename = df_N_product_data.rename(columns = {"c02":"Mea_hist","c03":"1-T1","c04":"1-T2","c05":"2-T1","c06":"2-T2","c07":"3-T1","c08":"3-T2","c09":"4-T1","c10":"4-T2"})
            df_N_product_data_allint = df_N_product_data_rename.astype({"1-T1":float})
            df_N_product_data_allint["thickness_1"] = np.where(df_N_product_data_allint['1-T1']>df_N_product_data_allint['1-T2'],df_N_product_data_allint['1-T1'], df_N_product_data_allint['1-T2'])
            df_N_product_data_allint["thickness_2"] = np.where(df_N_product_data_allint['2-T1']>df_N_product_data_allint['2-T2'],df_N_product_data_allint['2-T1'], df_N_product_data_allint['2-T2'])
            df_N_product_data_allint["thickness_3"] = np.where(df_N_product_data_allint['3-T1']>df_N_product_data_allint['3-T2'],df_N_product_data_allint['3-T1'], df_N_product_data_allint['3-T2'])
            #公差上下限
            df_N_product_data_allint["USL"] = ucl_side
            df_N_product_data_allint["LSL"] = lcl_side
            df_thickness_1 = df_N_product_data_allint.loc[:,["thickness_1"]]
            df_thickness_2 = df_N_product_data_allint.loc[:,["thickness_2"]]
            df_thickness_3 = df_N_product_data_allint.loc[:,["thickness_3"]]
            #全データ
            df_show_data = df_N_product_data_allint[["thickness_1","thickness_2","thickness_3","thickness_4","Mea_hist"]]
            df_show_data.fillna({"Mea_hist": 0},inplace=True)
            #工程能力計算(Base)
            df_within_tolerance_1 = df_thickness_1.query("@lcl_side < thickness_1 < @ucl_side")
            df_within_tolerance_2 = df_thickness_2.query("@lcl_side < thickness_2 < @ucl_side")
            df_within_tolerance_3 = df_thickness_3.query("@lcl_side < thickness_3 < @ucl_side")
            df_describe_1 = df_within_tolerance_1.describe()
            df_describe_2 = df_within_tolerance_2.describe()
            df_describe_3 = df_within_tolerance_3.describe()
            df_describe_all = pd.concat([df_describe_1,df_describe_2,df_describe_3],axis=1)
            #工程能力計算(標準偏差)
            std_1 = df_describe_all.at['std', 'thickness_1']
            std_2 = df_describe_all.at['std', 'thickness_2']
            std_3 = df_describe_all.at['std', 'thickness_3']
            std6_1 = std_1*6
            std6_2 = std_2*6
            std6_3 = std_3*6
            #工程能力計算(Cp)
            tolerance_width = ucl_side - lcl_side
            cp_1 = tolerance_width / std6_1
            cp_2 = tolerance_width / std6_2
            cp_3 = tolerance_width / std6_3
            cp_dataframe = pd.DataFrame({"thickness_1":[cp_1],"thickness_2":[cp_2],"thickness_3":[cp_3]})
            cp_dataframe.index = ["Cp"]
            #工程能力計算(Cpk)
            avg_1 = df_describe_all.at['mean', 'thickness_1']
            avg_2 = df_describe_all.at['mean', 'thickness_2']
            avg_3 = df_describe_all.at['mean', 'thickness_3']
            k1 = abs((ucl_side + lcl_side)/2 - avg_1) / (ucl_side + lcl_side)/2
            k2 = abs((ucl_side + lcl_side)/2 - avg_2) / (ucl_side + lcl_side)/2
            k3 = abs((ucl_side + lcl_side)/2 - avg_3) / (ucl_side + lcl_side)/2
            cpk_1 = (1-k1)*cp_1
            cpk_2 = (1-k2)*cp_2
            cpk_3 = (1-k3)*cp_3

            cp_dataframe = pd.DataFrame({"thickness_1":[cp_1,cpk_1],"thickness_2":[cp_2,cpk_2],"thickness_3":[cp_3,cpk_3]})
            cp_dataframe.index = ["Cp","Cpk"]
            df_add_cp = pd.concat([df_describe_all, cp_dataframe])


        elif number_of_pieces_int == 4:
            #データ処理
            df_N_product_data = df_product_data[["c02","c03","c04","c05","c06","c07","c08","c09","c10"]]
            df_N_product_data_rename = df_N_product_data.rename(columns = {"c02":"Mea_hist","c03":"1-T1","c04":"1-T2","c05":"2-T1","c06":"2-T2","c07":"3-T1","c08":"3-T2","c09":"4-T1","c10":"4-T2"})
            df_N_product_data_allint = df_N_product_data_rename.astype({"1-T1":float})
            df_N_product_data_allint["thickness_1"] = np.where(df_N_product_data_allint['1-T1']>df_N_product_data_allint['1-T2'],df_N_product_data_allint['1-T1'], df_N_product_data_allint['1-T2'])
            df_N_product_data_allint["thickness_2"] = np.where(df_N_product_data_allint['2-T1']>df_N_product_data_allint['2-T2'],df_N_product_data_allint['2-T1'], df_N_product_data_allint['2-T2'])
            df_N_product_data_allint["thickness_3"] = np.where(df_N_product_data_allint['3-T1']>df_N_product_data_allint['3-T2'],df_N_product_data_allint['3-T1'], df_N_product_data_allint['3-T2'])
            df_N_product_data_allint["thickness_4"] = np.where(df_N_product_data_allint['4-T1']>df_N_product_data_allint['4-T2'],df_N_product_data_allint['4-T1'], df_N_product_data_allint['4-T2'])           
            #公差上下限
            df_N_product_data_allint["USL"] = ucl_side
            df_N_product_data_allint["LSL"] = lcl_side
            df_thickness_1 = df_N_product_data_allint.loc[:,["thickness_1"]]
            df_thickness_2 = df_N_product_data_allint.loc[:,["thickness_2"]]
            df_thickness_3 = df_N_product_data_allint.loc[:,["thickness_3"]]
            df_thickness_4 = df_N_product_data_allint.loc[:,["thickness_4"]]
            #全データ
            df_show_data = df_N_product_data_allint[["thickness_1","thickness_2","thickness_3","thickness_4","Mea_hist"]]
            df_show_data.fillna({"Mea_hist": 0},inplace=True)
            #工程能力計算(Base)
            df_within_tolerance_1 = df_thickness_1.query("@lcl_side < thickness_1 < @ucl_side")
            df_within_tolerance_2 = df_thickness_2.query("@lcl_side < thickness_2 < @ucl_side")
            df_within_tolerance_3 = df_thickness_3.query("@lcl_side < thickness_3 < @ucl_side")
            df_within_tolerance_4 = df_thickness_4.query("@lcl_side < thickness_4 < @ucl_side")
            df_describe_1 = df_within_tolerance_1.describe()
            df_describe_2 = df_within_tolerance_2.describe()
            df_describe_3 = df_within_tolerance_3.describe()
            df_describe_4 = df_within_tolerance_4.describe()
            df_describe_all = pd.concat([df_describe_1,df_describe_2,df_describe_3,df_describe_4],axis=1)

            #工程能力計算(標準偏差)
            std_1 = df_describe_all.at['std', 'thickness_1']
            std_2 = df_describe_all.at['std', 'thickness_2']
            std_3 = df_describe_all.at['std', 'thickness_3']
            std_4 = df_describe_all.at['std', 'thickness_4']                     
            std6_1 = std_1*6
            std6_2 = std_2*6
            std6_3 = std_3*6
            std6_4 = std_4*6

            #工程能力計算(Cp)
            tolerance_width = ucl_side - lcl_side
            cp_1 = tolerance_width / std6_1
            cp_2 = tolerance_width / std6_2
            cp_3 = tolerance_width / std6_3
            cp_4 = tolerance_width / std6_4
            cp_dataframe = pd.DataFrame({"thickness_1":[cp_1],"thickness_2":[cp_2],"thickness_3":[cp_3],"thickness_4":[cp_4]})
            cp_dataframe.index = ["Cp"]

            #工程能力計算(Cpk)
            avg_1 = df_describe_all.at['mean', 'thickness_1']
            avg_2 = df_describe_all.at['mean', 'thickness_2']
            avg_3 = df_describe_all.at['mean', 'thickness_3']
            avg_4 = df_describe_all.at['mean', 'thickness_4']
            k1 = abs((ucl_side + lcl_side)/2 - avg_1) / (ucl_side + lcl_side)/2
            k2 = abs((ucl_side + lcl_side)/2 - avg_2) / (ucl_side + lcl_side)/2
            k3 = abs((ucl_side + lcl_side)/2 - avg_3) / (ucl_side + lcl_side)/2
            k4 = abs((ucl_side + lcl_side)/2 - avg_4) / (ucl_side + lcl_side)/2
            cpk_1 = (1-k1)*cp_1
            cpk_2 = (1-k2)*cp_2
            cpk_3 = (1-k3)*cp_3
            cpk_4 = (1-k2)*cp_4

            cp_dataframe = pd.DataFrame({"thickness_1":[cp_1,cpk_1],"thickness_2":[cp_2,cpk_2],"thickness_3":[cp_3,cpk_3],"thickness_4":[cp_4,cpk_4]})
            cp_dataframe.index = ["Cp","Cpk"]
            df_add_cp = pd.concat([df_describe_all, cp_dataframe])

        else :
            print("error")
    
    if uploaded_file is not None:
        #fig1(1pcs目)
        #fig1(Line)
        fig1_line = go.Figure()
        fig1_line.add_trace(go.Scatter(x=df_N_product_data_allint.index,
                         y=df_N_product_data_allint["thickness_1"],
                         mode='lines',
                         name='1pcs_Wall Thickness Line',
                        ),
              )
        
        fig1_line.add_trace(go.Scatter(x=df_N_product_data_allint.index,
                         y=df_N_product_data_allint["USL"],
                         mode='lines',
                         name='USL',
                         marker=dict(size=12,
                                    color="rgba(255,0,0,0.5)")
                        ),
              )       
        
        fig1_line.add_trace(go.Scatter(x=df_N_product_data_allint.index,
                         y=df_N_product_data_allint["LSL"],
                         mode='lines',
                         name='LSL',
                         marker=dict(size=12,
                                    color="rgba(0,255,0,0.5)")
                        ),
              )      
        fig1_line.update_layout(
            title="1pcs_Wall Thickness Line",
            xaxis_title= "Data",
            yaxis_title= "Thickness",
        )


        #fig1(hist)
        fig1_hist = go.Figure()
        fig1_hist.add_trace(go.Histogram(x=df_N_product_data_allint["thickness_1"]))
        fig1_hist.add_vrect(x0=ucl_side, x1=lcl_side,fillcolor="orange", opacity=0.3,)
        fig1_hist.update_layout(
            title="1pcs_Wall Thickness Hist",
            xaxis_title= "Data",
            yaxis_title= "Frequency",
        )

        #fig2(2pcs目)
        #fig2(Line)
        fig2_line = go.Figure()
        fig2_line.add_trace(go.Scatter(x=df_N_product_data_allint.index,
                         y=df_N_product_data_allint["thickness_2"],
                         mode='lines',
                         name='2pcs_Wall Thickness Line',
                        ),
              )
        
        fig2_line.add_trace(go.Scatter(x=df_N_product_data_allint.index,
                         y=df_N_product_data_allint["USL"],
                         mode='lines',
                         name='USL',
                         marker=dict(size=12,
                                    color="rgba(255,0,0,0.5)")
                        ),
              )        
        
        fig2_line.add_trace(go.Scatter(x=df_N_product_data_allint.index,
                         y=df_N_product_data_allint["LSL"],
                         mode='lines',
                         name='LCL',
                         marker=dict(size=12,
                                    color="rgba(0,255,0,0.5)"),
                        ),
              )
        fig2_line.update_layout(
            title="2pcs_Wall Thickness Line",
            xaxis_title= "Data",
            yaxis_title= "Thickness",
        )

        #fig2(Hist)
        fig2_hist = go.Figure()
        fig2_hist.add_trace(go.Histogram(x=df_N_product_data_allint["thickness_2"],
                                        name="2pcs_Wall Thickness Hist",
        ))
        fig2_hist.add_vrect(x0=ucl_side, x1=lcl_side,fillcolor="orange", opacity=0.3)
        fig2_hist.update_layout(
            title="2pcs_Wall Thickness Hist",
            xaxis_title= "Data",
            yaxis_title= "Frequency",
        )

        #fig2(Hist_all)
        fig_all = go.Figure()
        fig_all.add_trace(go.Histogram(x=df_N_product_data_allint["thickness_1"],
                                        name="1pcs_Wall Thickness Hist"

        ))
        fig_all.add_trace(go.Histogram(x=df_N_product_data_allint["thickness_2"],
                                        name="2pcs_Wall Thickness Hist"
        ))
        fig_all.update_layout(barmode="overlay")
        fig_all.update_traces(opacity=0.5)
        fig_all.update_layout(
            title="All_Wall Thickness Hist",
            xaxis_title= "Data",
            yaxis_title= "Frequency",
        )
        #fig3(3pcs目)
        #fig3(Line)
        fig3_line = go.Figure()
        fig3_line.add_trace(go.Scatter(x=df_N_product_data_allint.index,
                         y=df_N_product_data_allint["thickness_3"],
                         mode='lines',
                         name='3pcs_Wall Thickness Line',
                        ),
              )
        
        fig3_line.add_trace(go.Scatter(x=df_N_product_data_allint.index,
                         y=df_N_product_data_allint["USL"],
                         mode='lines',
                         name='USL',
                         marker=dict(size=12,
                                    color="rgba(255,0,0,0.5)")
                        ),
              )        
        
        fig3_line.add_trace(go.Scatter(x=df_N_product_data_allint.index,
                         y=df_N_product_data_allint["LSL"],
                         mode='lines',
                         name='LCL',
                         marker=dict(size=12,
                                    color="rgba(0,255,0,0.5)"),
                        ),
              )
        fig3_line.update_layout(
            title="3pcs_Wall Thickness Line",
            xaxis_title= "Data",
            yaxis_title= "Thickness",
        )

        #fig3(Hist)
        fig3_hist = go.Figure()
        fig3_hist.add_trace(go.Histogram(x=df_N_product_data_allint["thickness_3"],
                                        name="3pcs_Wall Thickness Hist",
        ))
        fig3_hist.add_vrect(x0=ucl_side, x1=lcl_side,fillcolor="orange", opacity=0.3)
        fig3_hist.update_layout(
            title="3pcs_Wall Thickness Hist",
            xaxis_title= "Data",
            yaxis_title= "Frequency",
        )

        #fig3(Hist_all)
        fig_all = go.Figure()
        fig_all.add_trace(go.Histogram(x=df_N_product_data_allint["thickness_1"],
                                        name="1pcs_Wall Thickness Hist"

        ))
        fig_all.add_trace(go.Histogram(x=df_N_product_data_allint["thickness_2"],
                                        name="2pcs_Wall Thickness Hist"
        ))
        fig_all.add_trace(go.Histogram(x=df_N_product_data_allint["thickness_3"],
                                        name="3pcs_Wall Thickness Hist"
        ))

        fig_all.update_layout(barmode="overlay")
        fig_all.update_traces(opacity=0.5)
        fig_all.update_layout(
            title="All_Wall Thickness Hist",
            xaxis_title= "Data",
            yaxis_title= "Frequency",
        )

        #fig4(4pcs目)
        #fig4(Line)
        fig4_line = go.Figure()
        fig4_line.add_trace(go.Scatter(x=df_N_product_data_allint.index,
                         y=df_N_product_data_allint["thickness_4"],
                         mode='lines',
                         name='4pcs_Wall Thickness Line',
                        ),
              )
        
        fig4_line.add_trace(go.Scatter(x=df_N_product_data_allint.index,
                         y=df_N_product_data_allint["USL"],
                         mode='lines',
                         name='USL',
                         marker=dict(size=12,
                                    color="rgba(255,0,0,0.5)")
                        ),
              )        
        
        fig4_line.add_trace(go.Scatter(x=df_N_product_data_allint.index,
                         y=df_N_product_data_allint["LSL"],
                         mode='lines',
                         name='LCL',
                         marker=dict(size=12,
                                    color="rgba(0,255,0,0.5)"),
                        ),
              )
        fig4_line.update_layout(
            title="4pcs_Wall Thickness Line",
            xaxis_title= "Data",
            yaxis_title= "Thickness",
        )

        #fig4(Hist)
        fig4_hist = go.Figure()
        fig4_hist.add_trace(go.Histogram(x=df_N_product_data_allint["thickness_4"],
                                        name="4pcs_Wall Thickness Hist",
        ))
        fig4_hist.add_vrect(x0=ucl_side, x1=lcl_side,fillcolor="orange", opacity=0.3)
        fig4_hist.update_layout(
            title="4pcs_Wall Thickness Hist",
            xaxis_title= "Data",
            yaxis_title= "Frequency",
        )

        #fig4(Hist_all)
        fig_all = go.Figure()
        fig_all.add_trace(go.Histogram(x=df_N_product_data_allint["thickness_1"],
                                        name="1pcs_Wall Thickness Hist"

        ))
        fig_all.add_trace(go.Histogram(x=df_N_product_data_allint["thickness_2"],
                                        name="2pcs_Wall Thickness Hist"
        ))
        fig_all.add_trace(go.Histogram(x=df_N_product_data_allint["thickness_3"],
                                        name="3pcs_Wall Thickness Hist"
        ))
        fig_all.add_trace(go.Histogram(x=df_N_product_data_allint["thickness_4"],
                                        name="4pcs_Wall Thickness Hist"
        ))

        fig_all.update_layout(barmode="overlay")
        fig_all.update_traces(opacity=0.5)
        fig_all.update_layout(
            title="All_Wall Thickness Hist",
            xaxis_title= "Data",
            yaxis_title= "Frequency",
        )



    if uploaded_file is not None:

        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"計画NO：{plan_no}")
        with col2:
            st.write(f"品番：{products_no}")
        with col3:
            st.write(f"取り個数：{number_of_pieces_int}ヶ")
        
        st.dataframe(df_show_data,width=1000,height=500)       
        st.dataframe(df_add_cp)

        
    st.write("-----------------------------------------------------------------------------------------------------------------")

    if uploaded_file is not None:
        if nikuatu_selected == "Number of 1pcs":
        
            st.plotly_chart(fig1_line, use_container_width=True)
            st.plotly_chart(fig1_hist, use_container_width=True)
            st.plotly_chart(fig_all, use_container_width=True)


        elif nikuatu_selected == "Number of 2pcs":
            st.plotly_chart(fig2_line, use_container_width=True)
            st.plotly_chart(fig2_hist, use_container_width=True)
            st.plotly_chart(fig_all, use_container_width=True)
        
        elif nikuatu_selected == "Number of 3pcs":
            st.plotly_chart(fig3_line, use_container_width=True)
            st.plotly_chart(fig3_hist, use_container_width=True)
            st.plotly_chart(fig_all, use_container_width=True)

        elif nikuatu_selected == "Number of 4pcs":
            st.plotly_chart(fig4_line, use_container_width=True)
            st.plotly_chart(fig4_hist, use_container_width=True)
            st.plotly_chart(fig_all, use_container_width=True)


if __name__ == "__main__":
    main()

