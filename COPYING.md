# DNS Formalization

This repository was copied from the artifacts provided to reproduce the results shown in the SIGCOMM'23 paper "A Formal Framework for End-to-End DNS Resolution", for which an MIT license is provided in LICENSE.

The following changes have been made in the directories ```Maude/src```, ```Maude/test```, and ```Maude/attack_exploration```:

commit 6f7f9037142179614290f0c123573a3466375255
Author: Christophe Merlin <Christophe.Merlin@raytheon.com>
Date:   Wed May 7 09:11:33 2025 -0400

    DNS: Add "last-mile" delay
    
    Add a separate delay for responses from the public DNS network into the
    requester, which may be in a corporate network (which presumably has
    different delay characteristics than the Internet).

commit ff28d95cefc1a57267e9698491440c8cb8c08dff
Author: Christophe Merlin <Christophe.Merlin@raytheon.com>
Date:   Tue Apr 15 08:49:26 2025 -0400

    DNS: Let forwarder match on out of order responses
    
    Let a DNS forwarder match on responses that are out of the order from
    which the queries went out.
    
    Prevent unmatch / early end of execution.

commit 20cf0efdea5a9130ffa5da5150a1a0241b80434b
Author: Joud Khoury <joud.khoury@rtx.com>
Date:   Tue Apr 1 18:50:00 2025 -0400

    bugfix

commit 3086d7fb4933d745a8a4375efcc5767be0804f60
Author: Joud Khoury <joud.khoury@rtx.com>
Date:   Mon Mar 31 12:58:58 2025 -0400

    remove Monitor from prob model and add forward rules for NS; remove print from nondet model

commit 24329dfa2e8d4402a3642ce630d97488f841f93b
Author: Joud Khoury <joud.khoury@rtx.com>
Date:   Wed Mar 12 14:00:34 2025 -0400

    remove monitor objects from the rewrite rules and config

commit cde930e3c47511ac3e883b796d365606f0654322
Author: Joud Khoury <joud.khoury@rtx.com>
Date:   Tue Mar 4 11:35:02 2025 -0500

    Allow specifying forward addr when initializing nameserver

commit 5c3e6ae19847f16bd73f51b4e0cbe2366bbb1e9f
Author: Joud Khoury <joud.khoury@rtx.com>
Date:   Tue Mar 4 11:19:51 2025 -0500

    Extend Nameserver actor to support fowarding
    
      - Forwarders block attribute and list to track forwarded queries
      - two new rules to handle forwarding of client queries and of responses to them

commit ec14c634befacd778e0c389be686a9133d642603
Author: Joud Khoury <joud.khoury@rtx.com>
Date:   Thu Feb 27 13:55:42 2025 -0500

    externalize PATH_TO_PROJ_DIR

commit 0faf9b0670b9e62776e079581bfc003d67d4bf99
Author: Joud Khoury <joud.khoury@rtx.com>
Date:   Wed Feb 26 08:50:44 2025 -0500

    refactor to use as package

