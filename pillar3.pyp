<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>JunheModels\pillar3.pyc</Name> <!--file.pyc-->  
        <Title>title</Title>
        <TextId>1000</TextId>
      <Version>1.0</Version>
      <ReadLastInput>False</ReadLastInput>
      <Interactor>False</Interactor>
    </Script>
    <Parameter>
        <Name>Picture</Name>
        <Value>pillar3.png</Value>
        <Orientation>Middle</Orientation>
        <ValueType>Picture</ValueType>
    </Parameter>
    <Page>
        <Name>Page1</Name>
        <Text>ConcreteMember</Text>
        <TextId>1001</TextId>   

        <Parameter>
            <Name>ConcreteMemberParameters</Name>
            <Text>Concrete Member Parameters</Text>
            <TextId>1101</TextId>
            <ValueType>Expander</ValueType>
            <Parameter>
                <Name>ConcreteGrade</Name>
                <Text>Concrete Grade</Text>
                <TextId>1102</TextId>
                <Value>1</Value>
                <ValueType>ReinfConcreteGrade</ValueType>
            </Parameter>
            <Parameter>
                <Name>Length</Name>
                <Text>Length</Text>
                <TextId>e_LENGTH</TextId>
                <Value>400</Value>
                <ValueType>length</ValueType>
                <MinValue>100</MinValue>
            </Parameter>

            <Parameter>
                <Name>Height</Name>
                <Text>Height</Text>
                <TextId>e_HEIGHT</TextId>
                <Value>2950</Value>
                <ValueType>length</ValueType>
                <MinValue>100</MinValue>
            </Parameter>
            <Parameter>
                <Name>Width</Name>
                <Text>Width</Text>
                <TextId>e_WIDTH</TextId>
                <Value>400</Value>
                <ValueType>length</ValueType>
                <MinValue>100</MinValue>
            </Parameter>
        </Parameter>
    </Page>

    <Page>
        <Name>Page2</Name>
        <Text>Stirrup</Text>
        <TextId>2001</TextId>      


        <Parameter>
            <Name>StirrupExpander</Name>
            <Text>Stirrup Parameter</Text>
            <TextId>2101</TextId>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>StirrupVisual</Name>
                <Text>Stirrup</Text>
                <TextId>2102</TextId>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
            </Parameter>
            <Parameter>
                <Name>MarkIndex_Stir</Name>
                <Text>Stir Steel Mark Index</Text>
                <TextId>2103</TextId>
                <Value>10</Value>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>StirSteelGrade</Name>
                <Text>Stirrup Steel Grade</Text>
                <TextId>2104</TextId>
                <Value>4</Value>
                <ValueType>ReinfSteelGrade</ValueType>
            </Parameter>
            <Parameter>
                <Name>StirDiameter</Name>
                <Text>Stirrup Diameter</Text>
                <TextId>2105</TextId>
                <Value>12</Value>
                <ValueType>ReinfBarDiameter</ValueType>
            </Parameter>
            <Parameter>
                <Name>StirSideCover</Name>
                <Text>Stirrup Side Cover</Text>
                <TextId>2106</TextId>
                <Value>20</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>StirFrontCover</Name>
                <Text>Stirrup Front Cover</Text>
                <TextId>2107</TextId>
                <Value>20</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>StirUpsCover</Name>
                <Text>Stirrup Up and Down Cover</Text>
                <TextId>2108</TextId>
                <Value>50</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>SleeveThick</Name>
                <Text>Sleeve Thick</Text>
                <TextId>2109</TextId>
                <Value>10</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>StirDenseDistance</Name>
                <Text>Stirrup Dense Distance</Text>
                <TextId>2110</TextId>
                <Value>100</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>StirSparseDistance</Name>
                <Text>Stirrup Sparse Distance</Text>
                <TextId>2111</TextId>
                <Value>200</Value>
                <ValueType>length</ValueType>
            </Parameter>



            <Parameter>
                <Name>SleeveAreaLength</Name>
                <Text>Sleeve Area Length</Text>
                <TextId>2112</TextId>
                <Value>100</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
            <Name>Hook_Angle</Name>
            <Text>Hook length</Text>
            <TextId>2119</TextId>
            <Value>90</Value>
            <ValueList>90|135</ValueList>
            <ValueType>IntegerComboBox</ValueType>
            <ValueType>angle</ValueType>
            </Parameter>

            <Parameter>
                <Name>BendingRoller</Name>
                <Text>Bending roller</Text>
                <TextId>2117</TextId>
                <Value>4.0</Value>
                <ValueType>ReinfBendingRoller</ValueType>
            </Parameter>

            <Parameter>
                <Name>StirExtend</Name>
                <Text>StirrupExtend</Text>
                <TextId>2114</TextId>
                <Value>Ture</Value>
                <ValueType>checkbox</ValueType>
            </Parameter>
            <Parameter>
                <Name>StirExtendSide</Name>
                <Text>Stirrup Extend Side</Text>
                <TextId>2115</TextId>
                <Value>1</Value>
                <ValueList>1|2|3|4</ValueList>
                <ValueType>IntegerComboBox</ValueType>
                <Visible>StirExtend == True</Visible>
            </Parameter>
            <Parameter>
                <Name>StirExtendLength</Name>
                <Text>Stirrup Extend Length</Text>
                <TextId>2116</TextId>
                <Value>500</Value>
                <ValueType>length</ValueType>
                <Visible>StirExtend == True</Visible>
            </Parameter>
        </Parameter>
    </Page>


    <Page>
        <Parameter>
            <Name>VerticalSteel</Name>
            <Text>Vertical Steel</Text>
            <TextId>3001</TextId>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>VertSteelVisual</Name>
                <Text>Vertical Steel Visual</Text>
                <TextId>3101</TextId>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
            </Parameter>
            <Parameter>
                <Name>MarkIndex_Vert</Name>
                <Text>Vert Steel Mark Index</Text>
                <TextId>3102</TextId>
                <Value>11</Value>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>VertSteelGrade</Name>
                <Text>Vertical Steel Grade</Text>
                <TextId>3103</TextId>
                <Value>4</Value>
                <ValueType>ReinfSteelGrade</ValueType>
            </Parameter>
            <Parameter>
                <Name>FootSteelDia</Name>
                <Text>Foot Steel Diameter</Text>
                <TextId>3109</TextId>
                <Value>14</Value>
                <ValueType>ReinfBarDiameter</ValueType>
            </Parameter>
            <Parameter>
                <Name>VertSteelDia</Name>
                <Text>Vertical Steel Diameter</Text>
                <TextId>3104</TextId>
                <Value>12</Value>
                <ValueType>ReinfBarDiameter</ValueType>
            </Parameter>
            <Parameter>
                <Name>VertNum</Name>
                <Text>Vertical Steel Num</Text>
                <TextId>3110</TextId>
                <Value>2</Value>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>VertDistance</Name>
                <Text>Vertical Steel Distance</Text>
                <TextId>3106</TextId>
                <Value>100</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>HoriSteelDia</Name>
                <Text>Horisental Steel Diameter</Text>
                <TextId>3105</TextId>
                <Value>12</Value>
                <ValueType>ReinfBarDiameter</ValueType>
            </Parameter>
            <Parameter>
                <Name>HoriNum</Name>
                <Text>Horisental Steel Num</Text>
                <TextId>3111</TextId>
                <Value>3</Value>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>HoriDistance</Name>
                <Text>Horizental Steel Distance</Text>
                <TextId>3112</TextId>
                <Value>60</Value>
                <ValueType>length</ValueType>
            </Parameter>
            <Parameter>
                <Name>VertExtendLength</Name>
                <Text>Vertical Extend Length</Text>
                <TextId>3107</TextId>
                <Value>300</Value>
                <ValueType>length</ValueType>
            </Parameter>
          <Parameter>
            <Name>Vert_steel_cover</Name>
            <Text>Vert_steel_cover</Text>
            <TextId>3113</TextId>
            <Value>50</Value>
            <ValueType>length</ValueType>
          </Parameter>
          <Parameter>
            <Name>Vert_steel_wanqu</Name>
            <Text>Vert_steel_wanqu</Text>
            <TextId>3114</TextId>
            <Value>90</Value>
            <ValueType>length</ValueType>
          </Parameter>


        </Parameter>
    </Page>

    <Page>
        <Parameter>
            <Name>TieSteel</Name>
            <Text>Tie Steel</Text>
            <TextId>4000</TextId>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>TieSteelVisual</Name>
                <Text>Tie Steel Visual</Text>
                <TextId>4101</TextId>
                <Value>True</Value>
                <ValueType>checkbox</ValueType>
            </Parameter>
            <Parameter>
                <Name>MarkIndex_Tie</Name>
                <Text>Tie Steel Mark Index</Text>
                <TextId>4102</TextId>
                <Value>12</Value>
                <ValueType>Integer</ValueType>
            </Parameter>
            <Parameter>
                <Name>TieSteelGrade</Name>
                <Text>Tie Steel Grade</Text>
                <TextId>4103</TextId>
                <Value>4</Value>
                <ValueType>ReinfSteelGrade</ValueType>
            </Parameter>
            <Parameter>
                <Name>TieSteelDia</Name>
                <Text>Tie Steel Diameter</Text>
                <TextId>4104</TextId>
                <Value>8</Value>
                <ValueType>ReinfBarDiameter</ValueType>
            </Parameter>

            <Parameter>
                <Name>TieSideHookAngle</Name>
                <Text>Tie Side Hook Angle</Text>
                <TextId>4108</TextId>
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
        <TextId>5001</TextId>      
        <Parameter>
            <Name>FormExpander</Name>
            <Text>Form Attribute</Text>
            <TextId>5101</TextId>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>Surface</Name>
                <Text>Surface Material</Text>
                <TextId>e_SURFACE</TextId>
                <Value>SMT\\concrete_exposed_concrete_holes</Value>
                <DisableButtonIsShown>False</DisableButtonIsShown>
                <ValueType>MaterialButton</ValueType>
            </Parameter>
<!--             <Parameter>
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