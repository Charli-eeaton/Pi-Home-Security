# Pi-Home-Security
An open project which uses a Pi as a home security device through the use of an Android app

### Required software ###
- Python3
- apache2
- pip3 Dominate

### Required Hardware ###
- Any Rapsberry pi
- Android Phone or tablet

To get the Python file to run on boot of the Raspberry Pi we just need to edit one file.
Start by opening your rc.local file with your text editor of choice or with the comand:

`sudo nano /etc/rc.local`

Once editing this file add the following to the bottom of the file:

`#Run python main on boot
python3 /var/www/html/main.py &
exit 0`

Now just reboot with the following and the main file will now be run on boot:

`sudo reboot now`
