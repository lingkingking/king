<?xml version="1.0" encoding="utf-8"?>
<Element>
  <Script>
    <Name>JunheModels\wall11.pyc</Name>
    <!--file.pyc-->
    <Title>wall</Title>
    <!-- <TextId>0001</TextId> -->
    <ReadLastInput>false</ReadLastInput>
    <Version>1.0</Version>
    <ReadLastInput>True</ReadLastInput>
    <Interactor>False</Interactor>
  </Script>
    <Parameter>
        <Name>Picture</Name>
        <Value>wall.png</Value>
        <Orientation>Middle</Orientation>
        <ValueType>Picture</ValueType>
    </Parameter>
    <Page>
        <Name>Wall</Name>
        <Text>Wall</Text>
        <TextId>1001</TextId>   

        <Parameter>
            <Name>WallComponent</Name>
            <Text>Wall Component</Text>
            <TextId>1101</TextId>
            <ValueType>Expander</ValueType>

            <!--Parameter--> 
                      
            <Parameter>
                <Name>Length</Name>
                <Text>Length</Text>
                <TextId>1102</TextId>
                <Value>2500.</Value>
                <ValueType>length</ValueType>
                <MinValue>100</MinValue>
                
            </Parameter>
            <Parameter>
                <Name>Height</Name>
                <Text>Height</Text>
                <TextId>1103</TextId>
                <Value>2950</Value>
                <ValueType>length</ValueType>
                <MinValue>100</MinValue>
            </Parameter>
            <Parameter>
                <Name>Width</Name>
                <Text>Width</Text>
                <TextId>1104</TextId>
                <Value>200</Value>
                <ValueType>length</ValueType>
                <MinValue>100</MinValue>
            </Parameter>
          <Parameter>
            <Name>PreHeight</Name>
            <Text>Precast Height</Text>
            <TextId>7006</TextId>
            <Value>100</Value>
            <ValueType>length</ValueType>
            <MinValue>100</MinValue>
          </Parameter>
            <Parameter>
                <Name>ConcreteGrade</Name>
                <Text>Concrete Grade</Text>
                <TextId>1105</TextId>
                <Value>1</Value>
                <ValueType>ReinfConcreteGrade</ValueType>
            </Parameter>
                  
        </Parameter>
     <Parameter>
        <Name>Hole_cover</Name>
        <Text>Hole cover</Text>
        <TextId>1990</TextId>
        <Value>20.</Value>
        <ValueType>length</ValueType>
      </Parameter> 
    <Parameter>
      <Name>window</Name>
      <Text>window</Text>
      <TextId>1901</TextId>
      <ValueType>expander</ValueType>          
      <Parameter>
        <Name>WLength</Name>
        <Text>WLength</Text>
        <TextId>1902</TextId>
        <Value>500</Value>
        <ValueType>length</ValueType>
        </Parameter>
        <Parameter>
          <Name>WHeight</Name>
          <Text>WHeight</Text>
          <TextId>1903</TextId>
          <Value>1800.</Value>
          <ValueType>length</ValueType> 
        </Parameter>
        <Parameter>
          <Name>oWmobilePosition</Name>
          <Text>oWmobilePosition</Text>
          <TextId>1904</TextId>
          <Value>700.</Value>
          <ValueType>length</ValueType>
        </Parameter>
        <Parameter>
          <Name>WmobilePosition</Name>
          <Text>WmobilePosition</Text>
          <TextId>1905</TextId>
          <Value>400.</Value>
          <ValueType>length</ValueType>
        </Parameter>
      <Parameter>
        <Name>WLength_d</Name>
        <Text>WLength_d</Text>
        <TextId>1906</TextId>
        <Value>500</Value>
        <ValueType>length</ValueType>
      </Parameter>
      <Parameter>
        <Name>oWmobilePosition_d</Name>
        <Text>oWmobilePosition_d</Text>
        <TextId>1907</TextId>
        <Value>0.</Value>
        <ValueType>length</ValueType>
      </Parameter>
      </Parameter>
                                              
    </Page>
    <Page>
        <Name>HorizontalSteel</Name>
        <Text>Horizontal Steel</Text>
        <TextId>1200</TextId>
        <Parameter>
            <Name>HorizontalSteel</Name>
            <Text>Horizontal Steel</Text>
            <TextId>1201</TextId>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>HoriSteelVisual</Name>
                <Text>Horizontal Steel Visual</Text>
                <TextId>1202</TextId>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
            </Parameter>
            <Parameter>
                <Name>MarkIndex_Hori</Name>
                <Text>Hori Steel Mark Index</Text>
                <TextId>1203</TextId>
                <Value>10</Value>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>HoriSteelGrade</Name>
                <Text>Horizontal Steel Grade</Text>
                <TextId>1204</TextId>
                <Value>3</Value>
                <ValueType>ReinfSteelGrade</ValueType>
            </Parameter>
            <Parameter>
                <Name>HoriSteelDia</Name>
                <Text>Horizontal Steel Diameter</Text>
                <TextId>1205</TextId>
                <Value>10</Value>
                <ValueType>ReinfBarDiameter</ValueType>
            </Parameter>
            <Parameter>
                <Name>HoriDistance</Name>
                <Text>Horizontal Steel Distance</Text>
                <TextId>1206</TextId>
                <Value>200</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>HoriFrontCover</Name>
                <Text>Horizontal Front Cover</Text>
                <TextId>1207</TextId>
                <Value>20</Value>
                <ValueType>length</ValueType>
            </Parameter>
          <Parameter>
            <Name>FrontCover</Name>
            <Text>Front Cover</Text>
            <TextId>1211</TextId>
            <Value>15</Value>
            <ValueType>length</ValueType>
          </Parameter>
            <Parameter>
                <Name>HoriTopCover</Name>
                <Text>Horizontal Top Cover</Text>
                <TextId>1208</TextId>
                <Value>20</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>HoriBottomCover</Name>
                <Text>Horizontal Bottom Cover</Text>
                <TextId>1209</TextId>
                <Value>20</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>HoriExtend</Name>
                <Text>Horizontal Steel Extend Length</Text>
                <TextId>1210</TextId>
                <Value>0</Value>
                <ValueType>length</ValueType>
            </Parameter>
         
    <!--<Parameter>
                <Name>HoriSteel_1</Name>
                <Text>Horizontal Steel 1 (group by two)</Text>
                <TextId>1300</TextId>
                <ValueType>Expander</ValueType>
                <Parameter>
                    <Name>HoriSideCover</Name>
                    <Text>Horizontal Side Cover</Text>
                    <Value>50</Value>
                    <TextId>1301</TextId>
                    <ValueType>length</ValueType>
                </Parameter>
            </Parameter> -->
            <Parameter>
                <Name>HoriSteel_2</Name>
                <Text>Horizontal Steel 2</Text>
                <TextId>1400</TextId>
                <ValueType>Expander</ValueType>
                <Parameter>
                    <Name>Degrees_HS2</Name>
                    <Text>90 Degrees_HS2</Text>
                    <TextId>1401</TextId>
                    <Value>false</Value>
                    <ValueType>checkbox</ValueType>
                </Parameter>
                <Parameter>
                    <Name>DegreesHook_HS2</Name>
                    <Text>90 Degrees Hook_HS2</Text>
                    <TextId>1402</TextId>
                    <Value>200</Value>
                    <ValueType>length</ValueType>
                    <Visible>Degrees_HS2 == True</Visible>
                </Parameter>
              <Parameter>
                <Name>LeftAnchor_HS2</Name>
                <Text>Left Anchor_HS2</Text>
                <TextId>1403</TextId>
                <Value>200</Value>
                <ValueType>length</ValueType>
              </Parameter>
              <Parameter>
                <Name>RightAnchor_HS2</Name>
                <Text>Right Anchor_HS2</Text>
                <TextId>1404</TextId>
                <Value>200</Value>
                <ValueType>length</ValueType>
              </Parameter>
               
            </Parameter>
        </Parameter>
    </Page>
    <Page>
        <Parameter>
            <Name>VerticalSteel</Name>
            <Text>Vertical Steel</Text>
            <TextId>1500</TextId>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>VertSteelVisual_q</Name>
                <Text>Vertical Steel Visual</Text>
                <TextId>1501</TextId>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
            </Parameter>
            <Parameter>
                <Name>MarkIndex_Vert</Name>
                <Text>Vert Steel Mark Index</Text>
                <TextId>1502</TextId>
                <Value>11</Value>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>VertSteelGrade</Name>
                <Text>Vertical Steel Grade</Text>
                <TextId>1503</TextId>
                <Value>3</Value>
                <ValueType>ReinfSteelGrade</ValueType>
            </Parameter>
            <Parameter>
                <Name>VertSteelDia</Name>
                <Text>Vertical Steel Diameter</Text>
                <TextId>1504</TextId>
                <Value>10</Value>
                <ValueType>ReinfBarDiameter</ValueType>
            </Parameter>
            <Parameter>
                <Name>VertSideCover</Name>
                <Text>Vertical Side Cover</Text>
                <TextId>1505</TextId>
                <Value>50</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>VertDistance</Name>
                <Text>Vertical Steel Distance</Text>
                <TextId>1506</TextId>
                <Value>200</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>Length_BA</Name>
                <Text>Bottom Anchor Length</Text>
                <TextId>1607</TextId>
                <Value>20</Value>
                <ValueType>length</ValueType>
            </Parameter>
        </Parameter>
        <Parameter>
                <Name>TopAnchor</Name>
                <Text>Top Anchor</Text>
                <TextId>1600</TextId>
                <ValueType>Expander</ValueType>

                <Parameter>
                    <Name>Length_TA</Name>
                    <Text>Top Anchor Length</Text>
                    <TextId>1601</TextId>
                    <Value>500</Value>
                    <ValueType>length</ValueType>
                </Parameter>
                <Parameter>
                    <Name>BendingAnchor</Name>
                    <Text>Bending Anchor</Text>
                    <TextId>1602</TextId>
                    <Value>False</Value>
                    <ValueType>checkbox</ValueType>
                </Parameter>
                <Parameter>
                    <Name>BendingAnchorArea</Name>
                    <Text>Bending Anchor Area</Text>
                    <TextId>1603</TextId>
                    <ValueType>Expander</ValueType>

                    <Parameter>
                        <Name>BendPosition</Name>
                        <Text>Bend Position</Text>
                        <TextId>1604</TextId>
                        <Value>150</Value>
                        <ValueType>length</ValueType>
                        <Visible>BendingAnchor == True</Visible>
                    </Parameter>
                    <Parameter>
                        <Name>BendLength</Name>
                        <Text>Bend Length</Text>
                        <TextId>1605</TextId>
                        <Value>150</Value>
                        <ValueType>length</ValueType>
                        <Visible>BendingAnchor == True</Visible>
                    </Parameter>
                    <Parameter>
                        <Name>BendWidth</Name>
                        <Text>Bend Width</Text>
                        <TextId>1606</TextId>
                        <Value>100</Value>
                        <ValueType>length</ValueType>
                        <Visible>BendingAnchor == True</Visible>
                    </Parameter>
                </Parameter>
          </Parameter>
    </Page>
    <Page>
        <Parameter>
               <Name>add_steel</Name>
               <Text>add_steel</Text>
               <TextId>2000</TextId>
              <ValueType>Expander</ValueType> 
              <Parameter>
                <Name>addSteelVisual</Name>
                <Text>add Steel Visual</Text>
                <TextId>2001</TextId>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
              </Parameter>
          <Parameter>
                <Name>addSteelDia</Name>
                <Text>addSteelDia</Text>
                <TextId>2002</TextId>
                <Value>8</Value>
                <ValueType>ReinfBarDiameter</ValueType>
              </Parameter>
          <Parameter>
                <Name>addSteelGrade</Name>
                <Text>addSteelGrade</Text>
                <TextId>2003</TextId>
                <Value>3</Value>
                <ValueType>ReinfSteelGrade</ValueType>
              </Parameter>
              <Parameter>
                <Name>add_Length</Name>
                <Text>add_Length</Text>
                <TextId>2004</TextId>
                <Value>600</Value>
                <ValueType>length</ValueType>
              </Parameter>
              <Parameter>
                  <Name>mobile_Length</Name>
                  <Text>mobile_Length</Text>
                  <TextId>2005</TextId>
                  <Value>70</Value>
                  <ValueType>length</ValueType>
              </Parameter>
          <Parameter>
            <Name>count</Name>
            <Text>count</Text>
            <TextId>2006</TextId>
            <Value>1</Value>
            <ValueType>length</ValueType>
          </Parameter>
        </Parameter> 
    </Page>

    <Page>
        <Parameter>
            <Name>TieSteel</Name>
            <Text>Tie Steel</Text>
            <TextId>1700</TextId>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>TieSteelVisual</Name>
                <Text>Tie Steel Visual</Text>
                <TextId>1701</TextId>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
            </Parameter>
            <Parameter>
                <Name>MarkIndex_Tie</Name>
                <Text>Tie Steel Mark Index</Text>
                <TextId>1702</TextId>
                <Value>12</Value>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>TieSteelGrade</Name>
                <Text>Tie Steel Grade</Text>
                <TextId>1703</TextId>
                <Value>3</Value>
                <ValueType>ReinfSteelGrade</ValueType>
            </Parameter>
            <Parameter>
                <Name>TieSteelDia</Name>
                <Text>Tie Steel Diameter</Text>
                <TextId>1704</TextId>
                <Value>8</Value>
                <ValueType>ReinfBarDiameter</ValueType>
            </Parameter>
            <Parameter>
                <Name>TieMode</Name>
                <Text>Tie Mode</Text>
                <TextId>1705</TextId>
                <Value>1</Value>
                <ValueList>1|2</ValueList>
                <ValueType>IntegerComboBox</ValueType>
            </Parameter>
           
            
             <Parameter>
                <Name>angle</Name>
                <Text>angle</Text>
                <TextId>1710</TextId>
                <Value>90</Value>
                <ValueList>90|135</ValueList>
                <ValueType>IntegerComboBox</ValueType>
                <Visible>TieSteelVisual == True </Visible>
            </Parameter>
        </Parameter>
    </Page>

  <Page>
    <Name>Page2</Name>
    <Text>Stirrup</Text>
    <TextId>7501</TextId>
    <Parameter>
      <Name>StirrupExpander</Name>
      <Text>Stirrup Parameter</Text>
      <TextId>7501</TextId>
      <ValueType>Expander</ValueType>
      <Parameter>
        <Name>StirVisual</Name>
        <Text>Stirrup Visual</Text>
        <TextId>7500</TextId>
        <Value>True</Value>
        <ValueType>checkbox</ValueType>
      </Parameter>
     
      <Parameter>
        <Name>ConcreteCover</Name>
        <Text>Concrete Cover</Text>
        <TextId>7503</TextId>
        <Value>25</Value>
        <ValueType>length</ValueType>
      </Parameter>
      <Parameter>
        <Name>StirSteelGrade</Name>
        <Text>Stirrup Steel Grade</Text>
        <TextId>7504</TextId>
        <Value>4</Value>
        <ValueType>ReinfSteelGrade</ValueType>
      </Parameter>
      <Parameter>
        <Name>StirDiameter</Name>
        <Text>Stirrup Diameter</Text>
        <TextId>7505</TextId>
        <Value>12</Value>
        <ValueType>ReinfBarDiameter</ValueType>
      </Parameter>
      <Parameter>
        <Name>HeadCover</Name>
        <Text>Head Cover</Text>
        <TextId>7506</TextId>
        <Value>50</Value>
        <ValueType>length</ValueType>
      </Parameter>
      <Parameter>
        <Name>EndCover</Name>
        <Text>End Cover</Text>
        <TextId>7507</TextId>
        <Value>50</Value>
        <ValueType>length</ValueType>
      </Parameter>
      <Parameter>
        <Name>DenStir</Name>
        <Text>Dense Stirrup</Text>
        <TextId>7512</TextId>
        <Value>False</Value>
        <ValueType>CheckBox</ValueType>
      </Parameter>
      <Parameter>
        <Name>StirDistance</Name>
        <Text>Stirrup Distance</Text>
        <TextId>7508</TextId>
        <Value>100</Value>
        <ValueType>length</ValueType>
        <Visible>DenStir == False</Visible>
      </Parameter>
      <Parameter>
        <Name>StirDenDistance</Name>
        <Text>Stirrup Dense Distance</Text>
        <TextId>7511</TextId>
        <Value>100</Value>
        <ValueType>length</ValueType>
      </Parameter>

      <Parameter>
        <Name>StirBendDia</Name>
        <Text>Stirrup Bending Roller Diameter</Text>
        <TextId>7509</TextId>
        <Value>2.</Value>
        <ValueType>length</ValueType>
      </Parameter>
      <Parameter>
        <Name>StirExtendLength</Name>
        <Text>Stirrup Extend Length</Text>
        <TextId>7510</TextId>
        <Value>100</Value>
        <ValueType>length</ValueType>
      </Parameter>
    </Parameter>
    <Parameter>
      <Name>Hook_Angle_L</Name>
      <Text>Hook length</Text>
      <TextId>7513</TextId>
      <Value>90</Value>
      <ValueList>90|135</ValueList>
      <ValueType>IntegerComboBox</ValueType>
      <ValueType>angle</ValueType>
    </Parameter>
  </Page>
  <Page>
    <Name>Page3</Name>
    <Text>LongitudinalBar</Text>
    <TextId>7001</TextId>
    <Parameter>
      <Name>AntiQuakeLevel</Name>
      <Text>Anti Quake Level</Text>
      <TextId>7004</TextId>
      <Value>1</Value>
      <ValueList>1|2</ValueList>
      <ValueType>IntegerComboBox</ValueType>
    </Parameter>
    <Parameter>
      <Name>LongitudinalBar</Name>
      <Text>Longitudinal Bar Parameter</Text>
      <TextId>7001</TextId>
      <ValueType>Expander</ValueType>
      <Parameter>
        <Name>LongbarVisual</Name>
        <Text>Long Bar Visual</Text>
        <TextId>7000</TextId>
        <Value>true</Value>
        <ValueType>checkbox</ValueType>
      </Parameter>

      <Parameter>
        <Name>BarSteelGrade</Name>
        <Text>Bar Steel Grade</Text>
        <TextId>7003</TextId>
        <Value>4</Value>
        <ValueType>ReinfSteelGrade</ValueType>
      </Parameter>
      
      
        <Parameter>
          <Name>FirstDia</Name>
          <Text>First Line Diameter</Text>
          <TextId>8502</TextId>
          <Value>12</Value>
          <Value>8</Value>
          <ValueType>ReinfBarDiameter</ValueType>
        </Parameter>
        <Parameter>
          <Name>FirstNum</Name>
          <Text>First Line Number</Text>
          <TextId>8503</TextId>
          <Value>2</Value>
          <ValueType>integer</ValueType>
        </Parameter>
        <Parameter>
          <Name>AnchorBend</Name>
          <Text>Anchor Bend</Text>
          <TextId>8505</TextId>
          <Value>False</Value>
          <ValueType>checkbox</ValueType>
        </Parameter>
        <Parameter>
          <Name>anchor</Name>
          <ValueType>separator</ValueType>
          <Visible>AnchorBend == True</Visible>
        </Parameter>

        <Parameter>
          <Name>AnchorHeadBend</Name>
          <Text>Anchor Head Bend</Text>
          <TextId>8506</TextId>
          <Value>False</Value>
          <ValueType>CheckBox</ValueType>
          <Visible>AnchorBend == True</Visible>
        </Parameter>
        <Parameter>
          <Name>AnchorTailBend</Name>
          <Text>Anchor Tail Bend</Text>
          <TextId>8507</TextId>
          <Value>False</Value>
          <ValueType>CheckBox</ValueType>
          <Visible>AnchorBend == True</Visible>
        </Parameter>
        <Parameter>
          <Name>SupportWidth</Name>
          <Text>Support Width</Text>
          <TextId>8508</TextId>
          <Value>400</Value>
          <ValueType>length</ValueType>
          <Visible>AnchorBend == True</Visible>
        </Parameter>

     

    </Parameter>
  </Page>
  <Page>
    <Name>Page4</Name>
    <Text>Waist and Tie</Text>
    <TextId>9501</TextId>
    <Parameter>
      <Name>WaistBar</Name>
      <Text>Waist Bar</Text>
      <TextId>9501</TextId>
      <ValueType>expander</ValueType>
      <Parameter>
        <Name>WaistVisual</Name>
        <Text>Waist Bar Visual</Text>
        <TextId>9500</TextId>
        <Value>true</Value>
        <ValueType>checkbox</ValueType>
      </Parameter>
      <Parameter>
        <Name>WaistBarGrade</Name>
        <Text>Waist Bar Steel Grade</Text>
        <TextId>9502</TextId>
        <Value>4</Value>
        <ValueType>ReinfSteelGrade</ValueType>
      </Parameter>
      <Parameter>
        <Name>WaistBarDia</Name>
        <Text>Waist Bar Diameter</Text>
        <TextId>9503</TextId>
        <Value>8</Value>
        <ValueType>ReinfBarDiameter</ValueType>
      </Parameter>
      <Parameter>
        <Name>WaistPosition</Name>
        <Text>Waist Bar Position</Text>
        <TextId>9504</TextId>
        <Value>150</Value>
        <ValueType>length</ValueType>
      </Parameter>
      <Parameter>
        <Name>WaistDistance</Name>
        <Text>Waist Bar Distance</Text>
        <TextId>9505</TextId>
        <Value>130</Value>
        <ValueType>length</ValueType>
      </Parameter>
      <Parameter>
        <Name>WaistNum</Name>
        <Text>Waist Bar Num</Text>
        <TextId>9506</TextId>
        <Value>3</Value>
        <ValueType>integer</ValueType>
      </Parameter>
      <Parameter>
        <Name>WaistHeadCover</Name>
        <Text>Waist Head Cover</Text>
        <TextId>9507</TextId>
        <Value>20</Value>
        <ValueType>length</ValueType>
      </Parameter>
    </Parameter>
  </Page>
  <Page>
    <Name>Page5</Name>
    <Text>TieBarVisual</Text>
    <TextId>9513</TextId>
    <Parameter>
      <Name>TieBarVisual</Name>
      <Text>TieBarVisualr</Text>
      <TextId>9513</TextId>
      <ValueType>expander</ValueType>
      <Parameter>
        <Name>TieBarVisual</Name>
        <Text>Tie Bar Visual</Text>
        <TextId>9512</TextId>
        <Value>true</Value>
        <ValueType>checkbox</ValueType>
      </Parameter>
      <Parameter>
        <Name>TieBarDia</Name>
        <Text>Tie Bar Diameter</Text>
        <TextId>9509</TextId>
        <Value>8</Value>
        <ValueType>ReinfBarDiameter</ValueType>
      </Parameter>
      <Parameter>
        <Name>TieBarGrade</Name>
        <Text>Tie Bar Grade</Text>
        <TextId>9510</TextId>
        <Value>4</Value>
        <ValueType>ReinfSteelGrade</ValueType>
      </Parameter>
      <Parameter>
        <Name>TieBarRatio</Name>
        <Text>Tie Bar Ratio</Text>
        <TextId>9511</TextId>
        <Value>2</Value>
        <ValueType>length</ValueType>
      </Parameter>
      <Parameter>
        <Name>Tie_Hook_Angle</Name>
        <Text>Tie Hook length</Text>
        <TextId>9512</TextId>
        <Value>90</Value>
        <ValueList>90|135</ValueList>
        <ValueType>IntegerComboBox</ValueType>
        <ValueType>angle</ValueType>
      </Parameter>
    </Parameter>
  </Page>
  
  <Page>
        <Name>Page2</Name>
        <Text>Stirrup</Text>
        <TextId>5001</TextId>      


        <Parameter>
            <Name>StirrupExpander</Name>
            <Text>Stirrup Parameter</Text>
            <TextId>5101</TextId>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>StirrupVisual</Name>
                <Text>Stirrup</Text>
                <TextId>5102</TextId>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
            </Parameter>
            <Parameter>
                <Name>MarkIndex_Stir</Name>
                <Text>Stir Steel Mark Index</Text>
                <TextId>5103</TextId>
                <Value>10</Value>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>StirSteelGrade</Name>
                <Text>Stirrup Steel Grade</Text>
                <TextId>5104</TextId>
                <Value>4</Value>
                <ValueType>ReinfSteelGrade</ValueType>
            </Parameter>
            <Parameter>
                <Name>StirDiameter</Name>
                <Text>Stirrup Diameter</Text>
                <TextId>5105</TextId>
                <Value>12</Value>
                <ValueType>ReinfBarDiameter</ValueType>
            </Parameter>
            <Parameter>
                <Name>StirSideCover</Name>
                <Text>Stirrup Side Cover</Text>
                <TextId>5106</TextId>
                <Value>20</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>StirFrontCover</Name>
                <Text>Stirrup Front Cover</Text>
                <TextId>5107</TextId>
                <Value>15</Value>
                <ValueType>length</ValueType>
            </Parameter>
            
          <Parameter>
            <Name>StirUnsCover</Name>
            <Text>Stirrun Up and Down Cover</Text>
            <TextId>5119</TextId>
            <Value>500</Value>
            <ValueType>length</ValueType>
          </Parameter>
          <Parameter>
            <Name>StirUpsCover</Name>
            <Text>Stirrup Up and Down Cover</Text>
            <TextId>5108</TextId>
            <Value>50</Value>
            <ValueType>length</ValueType>
          </Parameter>
            <Parameter>
                <Name>SleeveThick</Name>
                <Text>Sleeve Thick</Text>
                <TextId>5109</TextId>
                <Value>0</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>StirDenseDistance</Name>
                <Text>Stirrup Dense Distance</Text>
                <TextId>5110</TextId>
                <Value>100</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>StirSparseDistance</Name>
                <Text>Stirrup Sparse Distance</Text>
                <TextId>5111</TextId>
                <Value>200</Value>
                <ValueType>length</ValueType>
            </Parameter>



            <Parameter>
                <Name>SleeveAreaLength</Name>
                <Text>Sleeve Area Length</Text>
                <TextId>5112</TextId>
                <Value>140</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>DensAreaLength</Name>
                <Text>Sleeve Area Length</Text>
                <TextId>5113</TextId>
                <Value>800</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>TopDensAreaLength</Name>
                <Text>Top Sleeve Area Length</Text>
                <TextId>5118</TextId>
                <Value>1300</Value>
                <ValueType>length</ValueType>
            </Parameter>
          <Parameter>
            <Name>Hook_Angle</Name>
            <Text>Hook length</Text>
            <TextId>5119</TextId>
            <Value>90</Value>
            <ValueList>90|135</ValueList>
            <ValueType>IntegerComboBox</ValueType>
            <ValueType>angle</ValueType>
          </Parameter>
            <Parameter>
                <Name>BendingRoller</Name>
                <Text>Bending roller</Text>
                <TextId>5117</TextId>
                <Value>4.0</Value>
                <ValueType>ReinfBendingRoller</ValueType>
            </Parameter>
            <Parameter>
                <Name>rLength</Name>
                <Text>r Length</Text>
                <TextId>5120</TextId>
                <Value>100</Value>
                <ValueType>length</ValueType>
            </Parameter>

           
            
        </Parameter>
    </Page>


    <Page>
        <Parameter>
            <Name>VerticalSteel</Name>
            <Text>Vertical Steel</Text>
            <TextId>6001</TextId>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>VertSteelVisual</Name>
                <Text>Vertical Steel Visual</Text>
                <TextId>6101</TextId>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
            </Parameter>
            <Parameter>
                <Name>MarkIndex_Vert</Name>
                <Text>Vert Steel Mark Index</Text>
                <TextId>6102</TextId>
                <Value>11</Value>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>VertSteelGrade</Name>
                <Text>Vertical Steel Grade</Text>
                <TextId>6103</TextId>
                <Value>4</Value>
                <ValueType>ReinfSteelGrade</ValueType>
            </Parameter>
            <Parameter>
                <Name>FootSteelDia</Name>
                <Text>Foot Steel Diameter</Text>
                <TextId>6109</TextId>
                <Value>10</Value>
                <ValueType>ReinfBarDiameter</ValueType>
            </Parameter>
    
            <Parameter>
                <Name>HoriSteelDia</Name>
                <Text>Horisental Steel Diameter</Text>
                <TextId>6105</TextId>
                <Value>10</Value>
                <ValueType>ReinfBarDiameter</ValueType>
            </Parameter>
            <Parameter>
                <Name>HoriNum</Name>
                <Text>Horisental Steel Num</Text>
                <TextId>6111</TextId>
                <Value>3</Value>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>HoriDistance_z</Name>
                <Text>Horizental Steel Distance</Text>
                <TextId>6112</TextId>
                <Value>80</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>VertTopLength</Name>
                <Text>Vertical Extend Length</Text>
                <TextId>6107</TextId>
                <Value>250</Value>
                <ValueType>length</ValueType>
            </Parameter>
          <Parameter>
            <Name>VertTopLength_d</Name>
            <Text>Vertical Extend Length</Text>
            <TextId>6113</TextId>
            <Value>250</Value>
            <ValueType>length</ValueType>
          </Parameter>
          


        </Parameter>
    </Page>

    <Page>
        <Parameter>
            <Name>TieSteel</Name>
            <Text>Tie Steel</Text>
            <TextId>6200</TextId>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>TieSteelVisual_z</Name>
                <Text>Tie Steel Visual</Text>
                <TextId>6201</TextId>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
            </Parameter>
            <Parameter>
                <Name>MarkIndex_Tie</Name>
                <Text>Tie Steel Mark Index</Text>
                <TextId>6202</TextId>
                <Value>12</Value>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>TieSteelGrade</Name>
                <Text>Tie Steel Grade</Text>
                <TextId>6203</TextId>
                <Value>4</Value>
                <ValueType>ReinfSteelGrade</ValueType>
            </Parameter>
            <Parameter>
                <Name>TieSteelDia</Name>
                <Text>Tie Steel Diameter</Text>
                <TextId>6204</TextId>
                <Value>8</Value>
                <ValueType>ReinfBarDiameter</ValueType>
            </Parameter>

            <Parameter>
                <Name>TieSteelHook</Name>
                <Text>Tie Steel Hook Length</Text>
                <TextId>6207</TextId>
                <Value>80</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>TieSideHookAngle</Name>
                <Text>Tie Side Hook Angle</Text>
                <TextId>6208</TextId>
                <Value>90</Value>
                <ValueList>90|135</ValueList>
                <ValueType>IntegerComboBox</ValueType>
                <ValueType>angle</ValueType>
            </Parameter>
        </Parameter>
    </Page>
  
  
  

    <Page>
        <Name>Page2</Name>
        <Text>form</Text>
        <TextId>1800</TextId>
        <TextId>2001</TextId>      
        <Parameter>
            <Name>FormExpander</Name>
            <Text>Form Attribute</Text>
            <TextId>1801</TextId>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>Surface</Name>
                <Text>Surface Material</Text>
                <TextId>e_SURFACE</TextId>
                <Value>SMT\\concrete_exposed_concrete_holes</Value>
                <DisableButtonIsShown>False</DisableButtonIsShown>
                <ValueType>MaterialButton</ValueType>
            </Parameter>
           <!--  <Parameter>
                <Name>Layer</Name>
                <Text>Layer</Text>
                <TextId>e_LAYER</TextId>
                <Value>0</Value>
                <ValueType>Layer</ValueType>
            </Parameter>
            <Parameter>
                <Name>Pen</Name>
                <Text>Pen</Text>
                <TextId>2102</TextId>
                <Value>1</Value>
                <ValueType>Pen</ValueType>
            </Parameter>
            <Parameter>
                <Name>Stroke</Name>
                <Text>Stroke</Text>
                <TextId>2103</TextId>
                <Value>1</Value>
                <ValueType>Stroke</ValueType>
            </Parameter>
            <Parameter>
                <Name>Color</Name>
                <Text>Color</Text>
                <TextId>e_COLOR</TextId>
                <Value>1</Value>
                <ValueType>Color</ValueType>
            </Parameter>
            <Parameter>
                <Name>UseConstructionLineMode</Name>
                <Text>Construction Line</Text>  
                <TextId>2104</TextId>
                <Value>1</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter> -->
        </Parameter>            
    </Page>
</Element>