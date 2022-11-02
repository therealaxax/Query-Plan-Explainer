import interface

def main():
    interface.set_password()
    while True:
        try:
            interface.display()
            break
        except:
            print('Please check if query is correct and try again!')
            interface.error_message()
            pass

if __name__ == '__main__':
    main()