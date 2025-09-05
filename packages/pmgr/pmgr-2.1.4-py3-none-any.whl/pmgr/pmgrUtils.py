"""Usage:
    pmgrUtils.py save [<PV>]... [--cfg=C] [--parent=P] [-z|--zenity] [--objtype=O] [--hutch=H]
    pmgrUtils.py set [<PV>]... [--cfg=C] [-z|--zenity] [--objtype=O] [--hutch=H]
    pmgrUtils.py get [<PV>]... [-z|--zenity] [--objtype=O] [--hutch=H]
    pmgrUtils.py apply [<PV>]... [--cfg=C] [-z|--zenity] [--objtype=O] [--hutch=H]
    pmgrUtils.py diff [<PV>]...  [-z|--zenity] [--objtype=O] [--hutch=H]
    pmgrUtils.py find [<pattern>] [-s|--sensitive] [--objtype=O] [--hutch=H]
    pmgrUtils.py history --cfg=C [--start=datetime] [--end=datetime] [--csv=FILE]
    pmgrUtils.py [-h | --help]

Arguments
    <PV>           Motor PV(s). To do multiple motors, input the full PV
                   as the first argument, and then the numbers of the
                   rest as single entries, or in a range using a hyphen.
                   An example would be the following:

                       python pmgrUtils.py save SXR:EXP:MMS:01-05 10 12 14-16

                   This will apply the save function to motors 01, 02, 03,
                    04, 05, 10, 12, 14, 15 and 16.

    <pattern>      A pattern to match configuration names.  "." is any
                   character, "*" is any substring.  These can be quoted
                   with "\".  Matching is case-insensitive unless specified
                   otherwise.

Commands:
    save           Save live motor configuration
    set            Set the motor configuration
    get            Get the motor configuration
    apply          Apply the saved motor configuration to live values
    diff           Prints differences between pmgr and live values
    find           Find the configurations matching the given pattern
    history        Give the history of the configuration between the start
                   and end dates.  Dates can be one of three formats:
                   "2024-04-15 13:15", "3/24/2023", or "7/15/2022 15:27".
                   Save a full listing as a CSV file, or get a difference 
                   between successive changes.

Options:
    -v|--verbose   Print more info on active process
    -z|--zenity    Enables zenity pop-up boxes indicating when routines
                   have errors and when they have completed.
    -s|--sensitive Let the pattern match be case sensitive.
    -h|--help      Show this help message

pmgrUtils allows certain parameter manager transactions to be done using
the command line.

Hutches that are supported are listed in the pmgrUtils.cfg file. Adding
a hutch to the list of hutches there should enable pmgrUtils support for
that hutch (so long as it is already in the pmgr).

"""

import os

import psp.Pv as pv
from docopt import docopt
from pcdsutils.ext_scripts import get_hutch_name

from .pmgrAPI import pmgrAPI 

def getBasePV(PVArguments):
    """
    Returns the first base PV found in the list of PVArguments. It looks for the
    first colon starting from the right and then returns the string up until
    the colon. Takes as input a string or a list of strings.
    """
    if type(PVArguments) != list:
        PVArguments = [PVArguments]
    for arg in PVArguments:
        try:
            i = arg.rindex(":")
            return arg[: i + 1]
        except Exception:
            pass
    return None


def parsePVArguments(PVArguments):
    """
    Parses PV input arguments and returns a set of motor PVs that will have
    the pmgrUtil functions applied to.
    """

    PVs = set()
    if len(PVArguments) == 0:
        return None
    basePV = getBasePV(PVArguments)
    if not basePV:
        return None
    for arg in PVArguments:
        try:
            if "-" in arg:
                splitArgs = arg.split("-")
                if getBasePV(splitArgs[0]) == basePV:
                    PVs.add(splitArgs[0])
                start = int(splitArgs[0][-2:])
                end = int(splitArgs[1])
                while start <= end:
                    PVs.add(basePV + f"{start:02}")
                    start += 1
            elif len(arg) > 3:
                if getBasePV(arg) == basePV:
                    PVs.add(arg)
            elif len(arg) < 3:
                PVs.add(basePV + f"{int(arg):02}")
            else:
                pass
        except Exception:
            pass

    PVs = list(PVs)
    PVs.sort()
    return PVs


def message(z, d, msg, abort=True):
    if z:
        os.system("zenity --width 500 --{} --text='{}'".format(d, msg))
    if abort:
        exit(msg)
    else:
        print(msg)


def exc_to_str(action, PV, e):
    msg = "Failed to {} {}:\n".format(action, PV)
    if len(e.args) > 1:
        msg += "Error %d: %s\n" % (e.args[0], e.args[1])
    else:
        msg += "Error: %s\n" % e.args[0]
    return msg


def main():
    # Parse docopt variables
    args = docopt(__doc__)
    PVarguments = args["<PV>"]
    pattern = args["<pattern>"]
    if args["--zenity"] or args["-z"]:
        zenity = True
    else:
        zenity = False
    if args["--objtype"]:
        objType = args["--objtype"]
    else:
        objType = "ims_motor"
    if args["--hutch"]:
        hutch = args["--hutch"]
    else:
        hutch = get_hutch_name()
    if args["--parent"]:
        parent = args["--parent"]
    else:
        parent = hutch.upper()
    cfg = args["--cfg"]

    p = pmgrAPI(objType, hutch)

    if args["history"]:
        h = p.config_history(cfg, start=args['--start'], finish=args['--end'], diff=args['--csv'] is None)
        if args['--csv'] is None:
            for e in h:
                print('%s - %s config "%s"' % (e['date'].strftime("%d/%m/%Y %H:%M"), e['action'], e['name']))
                for k,v in e.items():
                    if k == 'date' or k == 'action' or k == 'name':
                        continue
                    print("    %s: %s" % (k, v))
        else:
            kl = [k for k in h[0].keys() if k not in ['date', 'action', 'name']]
            with open(args['--csv'], "w") as f:
                f.write("date,action,name,"+",".join(kl)+"\n")
                for e in h:
                    f.write('"%s","%s","%s",' % (e['date'].strftime("%d/%m/%Y %H:%M"), e['action'], e['name']))
                    for k in kl:
                        if type(e[k]) == str:
                            f.write('"%s"%s' % (e[k], "\n" if k == kl[-1] else ","))
                        else:
                            f.write('%s%s' % (e[k], "\n" if k == kl[-1] else ","))
        return 0

    if args["find"]:
        if args["--sensitive"] or args["-s"]:
            sensitive = True
        else:
            sensitive = False
        l = p.match_config(pattern, ci=not sensitive)
        if len(l) == 0:
            message(zenity, "error", 'No matches for "%s" found.' % pattern)
        else:
            message(
                zenity, "info", 'Possible matches for "%s":\n' % pattern + "\n".join(l)
            )
        return 0

    # Parse the PV input into full PV names, exit if none input
    if len(PVarguments) > 0:
        motorPVs = parsePVArguments(PVarguments)
    else:
        message(zenity, "error", "No PV input.  Try --help")

    # Sanity check arguments.
    if args["save"] and cfg and len(motorPVs) > 1:
        message(zenity, "error", "Save with --cfg must be for a single motor.")
    if args["set"] and cfg is None:
        message(zenity, "error", "Set must specify a configuration!")

    # Loop through each of the motorPVs
    msg = ""
    dialog = "info"
    for PV in motorPVs:
        # Print some motor info
        print(f"Motor PV:          {PV}")
        m_DESC = pv.get(PV + ".DESC")
        print(f"Motor description: {m_DESC}")

        if args["get"]:
            try:
                cfg = p.get_config(PV)
                msg += "Configuration of {} is {}.\n".format(PV, cfg)
            except Exception as e:
                msg += exc_to_str("get configuration of", PV, e)
                dialog = "error"
        if args["set"]:
            try:
                p.set_config(PV, cfgname=cfg)
                msg += "Configuration of {} successfully set to {}.\n".format(PV, cfg)
            except Exception as e:
                msg += exc_to_str("set configuration of", PV, e)
                dialog = "error"
        if args["apply"]:
            try:
                p.apply_config(PV, cfgname=cfg)
                msg += "Configuration of %s successfully applied.\n" % PV
            except Exception as e:
                msg += exc_to_str("apply configuration to", PV, e)
                dialog = "error"
        if args["diff"]:
            try:
                d = p.diff_config(PV)
                if len(d) == 0:
                    message(zenity, "info", "No differences for %s.\n" % PV)
                else:
                    m = "\n".join(
                        [
                            "    {}: actual={}, configured={}".format(
                                f, d[f][0], d[f][1]
                            )
                            for f in d.keys()
                        ]
                    )
                    message(
                        zenity,
                        "info",
                        "Differences for %s:\n" % PV + m + "\n",
                        abort=False,
                    )
            except Exception as e:
                message(
                    zenity,
                    "error",
                    exc_to_str("find differences of", PV, e),
                    abort=False,
                )
        if args["save"]:
            try:
                p.save_config(PV, cfgname=cfg, overwrite=True, parent=parent)
                msg += "Configuration of %s successfully saved.\n" % PV
            except Exception as e:
                msg += exc_to_str("save configuration of", PV, e)
                dialog = "error"
    if args["diff"]:
        exit()
    message(zenity, dialog, msg)


if __name__ == "__main__":
    main()
