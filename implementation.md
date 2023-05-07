# Forecasting ATT&CK Flow by Recommendation System based on APT
## How to implement the tool
## Tool details
Out tool has three functions.

* Map from log file to ATT&CK Technique
![画像1](https://user-images.githubusercontent.com/132205036/236394315-78705a0d-1c3b-4876-8063-022e5bdc7fb3.png)
Using a database created from the [Atomic red team](https://github.com/redcanaryco/atomic-red-team), our tool detect the ATT&CK Technique used by the attacker in the uploaded log file. The log is restricted to Sysmon log. Currently, mapping from logs to ATT&CK Technique is performed by pattern matching. This is not exhaustive and we plan to change to a different approach to mapping in the future.

* Visualize forecasting results
![画像2](https://user-images.githubusercontent.com/132205036/236395222-f2719211-225a-4815-b3fa-fe2f41189bb6.png)
From the detected ATT&CK Technique, it forecasts the Tehcnique that the attacker will possibly use in the future. The forecasted techniques are visualized together with the ATT&CK Tactic, enabling the user to identify the flow of the attack at each stage of the attack.
Red circle represent detected techniques, yellow circle represent forecasted techniques, cyan circle represent tactics.

* Output search queris of SIEM
![画像3](https://user-images.githubusercontent.com/132205036/236395645-1e387589-c68b-4dd7-a20b-801403d8bca5.png)
Outputs the Seach query of SIME associated with the forecasted ATT&CK Technique
Splunk is assumed as the SIME to be used.
Currently, the number of queries available for output is limited. This will be updated in the future.
