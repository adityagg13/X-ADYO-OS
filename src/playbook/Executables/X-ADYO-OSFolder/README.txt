X-ADYO OS - post-install tools
============================

View Install Report.cmd       Opens the install report (every change + undo notes).
Create Restore Point.cmd      Creates a fresh System Restore point now.
Open Backups Folder.cmd       Shows the pre-change snapshots (services, appx, tasks).
Undo X-ADYO OS.cmd              Restores service startup values and re-enables the
                              scheduled tasks X-ADYO OS disabled (partial undo).
Reinstall Microsoft Edge.cmd  Puts Edge back if you removed it.

Full rollback: run rstrui.exe and pick the "X-ADYO OS v1.0.0" restore point.

Nothing in this folder runs automatically. Every script is plain text and safe
to inspect before you run it.
