halonadm
============

Manage Halon (http://halon.se) SP servers easily.

installing
===============

Just use the pip ::

$ pip install halonadm

configuration
===============

Configuration file can be copied from ***/site-packages/halonadm/halonadm.conf** into **~/.halonadm.conf**.

Other paths beeing scanned for are ~/.config/halonadm/halonadm.conf and /etc/halonadm.conf.

usage
===============

Run halonadm --help for usable options and arguments.

qshape
------------------

**Example 1**: qshape - postfix qshape like output - info from queue ::

  $ halonadm qshape

    ,.-~*´¨¯¨`*·~-.¸-(  mailQueue  )-,.-~*´¨¯¨`*·~-.¸
                       T 5 10 20 40 80 160 320 640 1280 1280+
    domain      TOTAL 11 0  0  0  0  0   0   0   0    0    11
    example.com       11 0  0  0  0  0   0   0   0    0    11

**Example 2**: qshape with sender and verbose - info from history ::

  $ halonadm qshape -msv

    ,.-~*´¨¯¨`*·~-.¸-( mailHistory )-,.-~*´¨¯¨`*·~-.¸
                                                      T 5 10 20 40 80 160 320 640 1280 1280+
    domain                                    TOTAL 328 0  0  0  0  0   0   0  19   25   284
    example.se                                      122 0  0  0  0  0   0   0   0    0   122
     └─johan@example.se (122)
                                                                                        
    centerturf.net                                  107 0  0  0  0  0   0   0  12   20    75
     ├─webmail-unittests@centerturf.net (102)                                               
     ├─andreas@centerturf.net (3)                                                           
     └─sss@centerturf.net (2)                                                               
                                                                                        
    simonavikstrom.se                                34 0  0  0  0  0   0   0   0    0    34
     └─simona@simonavikstrom.se (34)                                                          
                                                                                        
    biona.net                                        28 0  0  0  0  0   0   0   7    5    16
     ├─gno@biona.net (24)                                                                   
     └─ajb@biona.net (4)                                                                    
                                                                                        
    ponies.re                                        28 0  0  0  0  0   0   0   0    0    28
     └─johan@ponies.re (28)                                                                   
                                                                                        
    <MAILER-DAEMON>                                   6 0  0  0  0  0   0   0   0    0     6
     └─None (6)                                                                             
                                                                                        
    simonvik.se                                       3 0  0  0  0  0   0   0   0    0     3
     └─simon@simonvik.se (3) 

mailq
------------------

**Example 3**: mailq - postfix mailq like output ::

  $ halonadm mailq

    msgid                                arrival time      sender/recipient
    1ee87321-3416-11e4-b1af-b8ca3afa9d73 09/04/14 11:30:34 johan@example.se
                                                           sdfwjsv@example.com
                                                            └───error: Hold list

    1db9ef95-3416-11e4-b1af-b8ca3afa9d73 09/04/14 11:30:32 johan@example.se
                                                           sdfwjsv@example.com
                                                            └───error: Hold list

    1d261e9f-3416-11e4-b1af-b8ca3afa9d73 09/04/14 11:30:31 johan@example.se
                                                           sdfwjsv@example.com
                                                            └───error: Hold list

view
------------------

**Example 4**: view - show a message from the queue ::

  $ halonadm view /storage/mail/processed/1e/1ee87321-3416-11e4-b1af-b8ca3afa9d73.eml halonsp1.example.com

    Received: from private.example.com (unknown [10.246.192.112])
            by halonsp1.example.com (Halon Mail Gateway) with ESMTPSA
            for <sdfwjsv@example.com>; Thu, 28 Aug 2014 16:16:28 +0200 (CEST)
    Date: Thu, 28 Aug 2014 14:17:27 +0000
    To: sdfwjsv@example.com
    From: johan@example.se
    Subject: test Thu, 28 Aug 2014 14:17:27 +0000
    X-Mailer: swaks v20100211.0 jetmore.org/john/code/swaks/

    This is a test mailing
