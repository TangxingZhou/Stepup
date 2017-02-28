*** Settings ***
Documentation    Reserve Testlines on Cloud
Library     Selenium2Library
Library     DateTime

*** Variables ***
${USER}                 tangxinz
${PASSWORD}             DHUztx1279
@{TESTLINE_TYPE}        124             #CLOUD_ASB_F(Value=124)
@{DURATION}             240             #4h
@{ENB_BUILD}            9876            #FL00_FSM3_9999_161031_033736:base(Value=9456)
${ROBOTLTE_REVISION}    HEAD
@{ENB_REQUIRED_STATE}   1069            #commissioned

*** Test Cases ***
Test title
    [Tags]    DMZ
    ${sleep}=   Wait Tomorrow At 7 am
    Sleep   ${sleep}
    Open Browser                http://asb-cm.wroclaw.nsn-rdnet.net/  chrome
    Click Element               tag=a
    Click Element               xpath=//ul[@class='nav navbar-nav']/li/a[@href='/reservation/create']
    Input text                  xpath=//input[@id='id_username']            ${USER}
    Input text                  xpath=//input[@id='id_password']            ${PASSWORD}
    Click Element               xpath=//input[@value='Login']
    Execute Javascript          document.getElementById('id_testline_type').style.display='block';
    Select From List By Value   css=select#id_testline_type                 @{TESTLINE_TYPE}
    Select From List By Value   xpath=//select[@id='id_duration']           @{DURATION}
    Execute Javascript          document.getElementById('id_enb_build').style.display='block';
    Select From List By Value   css=select#id_enb_build                     @{ENB_BUILD}
    Input Text                  xpath=//input[@id='id_robotlte_revision']   ${ROBOTLTE_REVISION}
    Select From List By Value   xpath=//select[@id='id_state']              @{ENB_REQUIRED_STATE}
    Click Element               xpath=//input[@value='Reserve']
    Close Browser

*** Keywords ***
Wait Tomorrow At 7 am
    ${now}=             Get Current Date
    ${new_now}=         Convert Date                ${now}                  datetime
    ${year}=            Convert To String           ${new_now.year}
    ${month}=           Convert To String           ${new_now.month}
    ${day}=             Convert To String           ${new_now.day}
    ${next_day_str}=    Set Variable                ${year}-${month}-${day} 07:00:00.000
    ${next_day_time}=   Convert Date                ${next_day_str}         datetime
    ${next_day}=        Add Time To Date            ${next_day_time}        1 days
    ${wait_seconds}=    Subtract Date From Date     ${next_day}             ${now}
    ${wait}=            Convert To Integer          ${wait_seconds}
    [Return]  ${wait}
