import os, sys, asyncio
# import faulthandler

# faulthandler.enable()

# if 'CASROOT' in os.environ:
#     del os.environ['CASROOT']

# if sys.platform == 'win32':
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.__main__ import main

if __name__ == '__main__':
    main()
