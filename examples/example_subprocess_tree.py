import asyncio

from ansible_sdk.executors import AnsibleSubprocessJobExecutor, AnsibleSubprocessJobOptions
from ansible_sdk import AnsibleJobDef



async def run_one_stdout(executor, executor_options, job_options={}):
    """
    Run a single playbook job with several hosts and echo the display output as it arrives
    """
    playbook = job_options.get('playbook', None)

    try:
        job_def = AnsibleJobDef(
            playbook=playbook,
            data_dir='datadir',
        )
        job_status = await executor.submit_job(job_def, executor_options)

        tree = []
        def check_add(tree, line):
            for element in tree:
                if line['parent_uuid'] == element['uuid']:
                    element['children'].append({'uuid': line['uuid'], 'event': line['event'], 'children': []})
                else:
                    check_add(element['children'], line)

        event_ident = None
        async for line in job_status.events:
            if 'runner_ident' in line:
                event_ident = line['runner_ident']

            if 'parent_uuid' not in line:
                tree.append({'uuid': line['uuid'], 'event': line['event'], 'children': []})
            else:
                check_add(tree, line)


        await job_status
        from pprint import pprint
        print("%s =>" % event_ident)
        pprint(tree)
    finally:
        print('all done, exiting')

async def main():
    executor = AnsibleSubprocessJobExecutor()
    executor_options = AnsibleSubprocessJobOptions()
    job_options = {
        'playbook': 'pb.yml'
    }

    await run_one_stdout(executor, executor_options, job_options=job_options)


if __name__ == '__main__':
    asyncio.run(main())

