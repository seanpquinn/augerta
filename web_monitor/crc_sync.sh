#!/bin/sh
#VERY IMPORTANT: Transfers happen over ssh. To run automatically
#the CRC machine MUST have imogen's public key in the authorized_key list!

#Update CRC T3 data
rsync -av -e "ssh" /home/augta/data/south/t3/ augerta@deltacrc.dip.jp:/home/augerta/disk/south/t3/
sleep 2s

#Update CRC T2 data
rsync -av -e "ssh" /home/augta/data/south/t2/ augerta@deltacrc.dip.jp:/home/augerta/disk/south/t2/
sleep 2s

#Update CRC sulog data
rsync -av -e "ssh" /home/augta/data/south/sulog/ augerta@deltacrc.dip.jp:/home/augerta/disk/south/sulog/
sleep 2s

#Update coincidence data
rsync -av -e "ssh" /home/augta/data/coincidence/ augerta@deltacrc.dip.jp:/home/augerta/disk/coincidence/
sleep 2s

#Update TA timestamp data
rsync -av -e "ssh" /home/augta/data/ta/ augerta@deltacrc.dip.jp:/home/augerta/disk/ta/

#Update North monitoring data
rsync -av -e "ssh" /home/augta/data/north/Monitor/ augerta@deltacrc.dip.jp:/home/augerta/disk/north/Monitor/
sleep 2s

#Processed data sync
rsync -av --exclude '*.CTAG.gz' -e "ssh" /var/www/html/monitor/data/global_south/ augerta@deltacrc.dip.jp:/home/augerta/disk/processed/global/south/
sleep 2s
rsync -av --exclude '*.CTAG.gz' -e "ssh" /var/www/html/monitor/data/global_north/ augerta@deltacrc.dip.jp:/home/augerta/disk/processed/global/north/
