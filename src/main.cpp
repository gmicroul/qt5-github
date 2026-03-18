#include <QApplication>
#include <QWidget>
#include <QFormLayout>
#include <QLineEdit>
#include <QPushButton>
#include <QMessageBox>
#include <QSettings>
#include <QDialog>
#include "uploader.h"

// --- Settings dialog ----------------------------------------------------
class SettingsDialog : public QDialog {
    Q_OBJECT
public:
    SettingsDialog(QWidget *parent = nullptr)
        : QDialog(parent), urlEdit(new QLineEdit(this)),
          userEdit(new QLineEdit(this)), patEdit(new QLineEdit(this)) {
        setWindowTitle("Settings");
        urlEdit->setPlaceholderText("https://github.com/user/repo.git");
        patEdit->setEchoMode(QLineEdit::Password);

        QFormLayout *lay = new QFormLayout(this);
        lay->addRow("Remote URL:", urlEdit);
        lay->addRow("Username:", userEdit);
        lay->addRow("PAT:", patEdit);

        QHBoxLayout *btnLay = new QHBoxLayout;
        QPushButton *ok = new QPushButton("OK", this);
        QPushButton *cancel = new QPushButton("Cancel", this);
        btnLay->addStretch();
        btnLay->addWidget(ok);
        btnLay->addWidget(cancel);
        lay->addLayout(btnLay);

        connect(ok, &QPushButton::clicked, this, &QDialog::accept);
        connect(cancel, &QPushButton::clicked, this, &QDialog::reject);
    }

    QString remoteUrl() const { return urlEdit->text(); }
    QString user() const { return userEdit->text(); }
    QString pat() const { return patEdit->text(); }

private:
    QLineEdit *urlEdit;
    QLineEdit *userEdit;
    QLineEdit *patEdit;
};

int main(int argc, char *argv[]){
    QApplication a(argc, argv);

    QSettings cfg("MyCompany","GitHubUploader");
    QString remoteUrl = cfg.value("remoteUrl","https://github.com/your-user/your-repo.git").toString();
    QString user = cfg.value("user","").toString();
    QString pat = cfg.value("pat","").toString();

    QWidget w;
    w.setWindowTitle("GitHub Uploader");
    QFormLayout layout(&w);

    QLineEdit *userEdit = new QLineEdit(&w);
    QLineEdit *passEdit = new QLineEdit(&w);
    passEdit->setEchoMode(QLineEdit::Password);

    layout.addRow("Username:", userEdit);
    layout.addRow("Password (PAT):", passEdit);

    QPushButton *uploadBtn = new QPushButton("Upload →", &w);
    layout.addWidget(uploadBtn);

    QPushButton *settingsBtn = new QPushButton("⚙️ Settings", &w);
    layout.addWidget(settingsBtn);

    QObject::connect(settingsBtn, &QPushButton::clicked, [&](){
        SettingsDialog dlg(&w);
        dlg.urlEdit->setText(remoteUrl);
        dlg.userEdit->setText(user);
        dlg.patEdit->setText(pat);
        if(dlg.exec() == QDialog::Accepted){
            remoteUrl = dlg.remoteUrl();
            user = dlg.user();
            pat = dlg.pat();
            cfg.setValue("remoteUrl", remoteUrl);
            cfg.setValue("user", user);
            cfg.setValue("pat", pat);
        }
    });

    QObject::connect(uploadBtn, &QPushButton::clicked, [&](){
        QString u = userEdit->text();
        QString p = passEdit->text();
        if(u.isEmpty() || p.isEmpty()){
            QMessageBox::warning(&w, "Missing info", "Username & password required.");
            return;
        }
        Uploader up(u, p, remoteUrl);
        if(!up.upload()){
            QMessageBox::critical(&w, "Upload failed", up.lastError());
        } else {
            QMessageBox::information(&w, "Success", "Repository pushed to GitHub!");
        }
    });

    w.show();
    return a.exec();
}

#include "main.moc"
