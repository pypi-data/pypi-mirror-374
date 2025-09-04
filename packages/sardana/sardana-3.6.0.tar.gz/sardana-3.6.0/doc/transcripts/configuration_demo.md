Hello Sardana dancers!

1. In this video I will demonstrate you how to use the sardana **Command Line Interface** tool to configure a Sardana system.

2. Sardana is based on Tango and uses client - server architecture.
   Its server configuration is stored in a Tango DB.

3. The central point of the configuration tool is the **Sardana configuration format** based on YAML.
   The configuration tool offers a set of commands, for example **dump** and **load**.

4. To prepare the demo I:
   - create a Sardana server called demo1: `Sardana demo1`
   - start a Spock session and populates the server with simulated elements using: `sar_demo` macro

5. Let's try the Sardana configuration tool.
    
6. First I **dump** the server info using the dump command: ``sardanactl config dump``
   As you can observe the info is printed on the stdout. 
   Now, I redirect it into a file: `sardanactl config dump > demo1.yaml`

7. Let's imagine we need to change some configuration. For that I edit the YAML file:
   - change physical role of slit pseudo motor controller: mot02 -> mot03
   - remove ct04 channel from the measurement group
    
8. To **load** the new configuration I use the load command: `sardanactl config load demo1.yaml`
   - On the stdout we can see the summary of changes.
   This command, by default runs in dry-run mode, and does not perform any action on the Tango DB yet.
   - To really apply the changes I need to use the ``--write`` option.

9. Now, I restart the server to see if the changes were correctly applied.
   - to check the slit pseudomotor controller I use the sar_info macro ``sar_info gap01``
   - to check the measurement group I use the get_meas_conf macro ``get_meas_conf``

10. Now, I add some comments to the YAML file to better describe my configuration.

11. Meanwhile, let's change the configuration of my Sardana system at runtime, I:
   - set motor offset: `set_user_pos mot01 10`
   - disable ct03 in the measurement group e.g. using the ``expconf`` widget

12. Now I perform an **update**, so both the runtime changes and my YAML file comments are preserved.
    For this I use the original YAML file and update it with the dump of the Tango DB configuration which contains my runtime configuration changes.
    `sardanactl config dump | sardanactl config update demo1.yaml -`
    I chain the dump command stdout into the stdin of the update command using the "-" (dash) argument:
    And finally I store it in a new file.
    `sardanactl config dump | sardanactl config update demo1.yaml - > demo1_new.yaml`
    The update command also takes care about preserving the order of the YAML file.

13. To check differences between these two files I use the **diff** command:
    `sardanactl config diff demo1.yaml demo1_new.yaml`

14. To finish the demo, let's try the **validation** feature:
    I intentionally introduce an error in the new configuration file - I set a wrong name of ct02 instrument
    and validate it with the validate command: `sardanactl config validate demo1_new.yaml`. And it detects the error.
    
That's it! Thank you for your atention!
