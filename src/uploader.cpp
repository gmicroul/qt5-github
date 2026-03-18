#include "uploader.h"
#include <QProcess>
#include <QDir>
#include <QDebug>

Uploader::Uploader(const QString &user, const QString &pat, const QString &remoteUrl)
    : m_user(user), m_pat(pat), m_remoteUrl(remoteUrl), m_error("") {}

bool Uploader::upload()
{
    // Prepare repository path (current directory)
    QDir repoDir(QDir::currentPath());

    // init repo if missing
    if(!repoDir.exists(".git")){
        QProcess initProc;
        initProc.setProgram("git");
        initProc.setArguments({"init"});
        initProc.setWorkingDirectory(repoDir.absolutePath());
        initProc.start();
        if(!initProc.waitForFinished(30000)) { m_error = "git init timed out"; return false; }
    }

    // Set remote (replace existing if needed)
    QProcess remoteProc;
    remoteProc.setProgram("git");
    remoteProc.setArguments({"remote", "set-url", "origin", m_remoteUrl});
    remoteProc.setWorkingDirectory(repoDir.absolutePath());
    remoteProc.start();
    if(!remoteProc.waitForFinished(30000)) { m_error = "git remote set-url failed"; return false; }

    // Commit (if any changes)
    QProcess addProc;
    addProc.setProgram("git");
    addProc.setArguments({"add", "."});
    addProc.setWorkingDirectory(repoDir.absolutePath());
    addProc.start();
    addProc.waitForFinished(30000);

    QProcess commitProc;
    commitProc.setProgram("git");
    commitProc.setArguments({"commit", "-m", "\"Auto commit\""});
    commitProc.setWorkingDirectory(repoDir.absolutePath());
    commitProc.start();
    commitProc.waitForFinished(30000);

    // Push
    QProcess pushProc;
    pushProc.setProgram("git");
    pushProc.setArguments({"push", "-u", "origin", "master"});
    pushProc.setWorkingDirectory(repoDir.absolutePath());
    pushProc.start();
    if(!pushProc.waitForFinished(60000)) { m_error = "git push timed out"; return false; }
    if(pushProc.exitStatus() != QProcess::NormalExit || pushProc.exitCode() != 0){
        m_error = pushProc.readAllStandardError();
        return false;
    }
    return true;
}

QString Uploader::lastError() const { return m_error; }
