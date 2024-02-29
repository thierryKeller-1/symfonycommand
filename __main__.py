from argparse import ArgumentParser
from command import SymfonyCommand

parser = ArgumentParser('run symfony command automatically')
parser.add_argument('-a', '--action',dest='action', help="action to be launched [run or clear-log or setup]", required=True)
parser.add_argument('-np', '--number-of-page',dest='number_of_page', default=1, help='number of page')
parser.add_argument('-nd', '--number-of-data',dest='number_of_data', help='number of data')

args = parser.parse_args()


ARG_INFO = ['-a']

if __name__=='__main__':
    prog = SymfonyCommand()
    if args.action:
        match(args.action):
            case 'start':
                if args.number_of_page and args.number_of_data:
                    prog.set_number_of_page(args.number_of_page)
                    prog.set_number_of_data(args.number_of_data)
                prog.create_log()
                prog.load_log()
                prog.run()

            case 'clear-log':
                prog.clear_log()
            case 'setup':
                prog.setup()
    else:
        print("   ==> command argument not completed")
