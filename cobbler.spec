# TODO
# - avoid using defattr() and giving too much dirs/files to http
# - webapps
# - FHS in web paths
# - bash-completions
# - logrotate
%define	subver	beta5
%define	rel		0.10
Summary:	Boot server configurator
Summary(pl.UTF-8):	Konfiguracja serwera startującego
Name:		cobbler
Version:	2.4.0
Release:	0.%{subver}.%{rel}
License:	GPL v2+
Group:		Applications/System
Source0:	https://github.com/cobbler/cobbler/archive/%{name}-%{version}-%{subver}.tar.gz
# Source0-md5:	f0b63f64d679e3ee547de2d97b74e681
Source1:	%{name}-apache.conf
URL:		http://www.cobblerd.org/
BuildRequires:	python-PyYAML
BuildRequires:	python-cheetah
BuildRequires:	python-devel
BuildRequires:	python-setuptools
Requires:	apache-mod_wsgi
Requires:	createrepo
#Requires:	genisoimage
Requires:	python-PyYAML
Requires:	python-augeas
Requires:	python-cheetah
Requires:	python-netaddr
Requires:	python-simplejson
Requires:	python-urlgrabber
Requires:	rsync
Requires:	tftpdaemon
Requires:	yum-utils
Requires(post,preun):	/sbin/chkconfig
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_appdir		/var/www/cobbler
%define		_cgibindir	/var/www/cgi-bin

#define		_appdir		%{_datadir}/%{name}
#define     _cgibindir	%{_prefix}/lib/cgi-bin/%{name}

%description
Cobbler is a network boot and update server. Cobbler supports PXE,
provisioning virtualized images, and reinstalling existing Linux
machines. The last two modes require a helper tool called 'koan' that
integrates with Cobbler. Cobbler's advanced features include importing
distributions from DVDs and rsync mirrors, kickstart templating,
integrated yum mirroring, and built-in DHCP Management. Cobbler has a
Python API for integration with other GPL systems management
applications.

%description -l pl.UTF-8
Cobbler to sieciowy serwer do uruchamiania i uaktualniania komputerów.
Obsługuje PXE, udostępnianie wirtualizowanych obrazów i reinstalowanie
istniejących maszyn linuksowych. Dwa ostatnie tryby wymagają pakietu
pomocniczego o nazwie "koan", integrującego się z Cobblerem.
Zaawansowane możliwości Cobblera obejmują importowanie dystrybucji z
płyt DVD i mirrorów rsynca, szablony uruchamiania, zintegrowane
mirrorowanie repozytoriów yuma oraz wbudowane zarządzanie DHCP.
Cobbler ma API w Pythonie do integracji z innymi aplikacjami
zarządzającymi na licencji GPL.

%package web
Summary:	Web interface for Cobbler
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}
Requires:	apache-mod_ssl
Requires:	apache-mod_wsgi
Requires:	python-django >= 1.1.2

%description web
Web interface for Cobbler that allows visiting
<http://server/cobbler_web> to configure the install server.

%package -n koan
Summary:	Helper tool that performs cobbler orders on remote machines
Group:		Applications/System
Requires:	python-simplejson
Requires:	python-virtinst

%description -n koan
Koan stands for kickstart-over-a-network and allows for both network
installation of new virtualized guests and reinstallation of an
existing system. For use with a boot-server configured with Cobbler

%prep
%setup -q -n %{name}-%{name}-%{version}-%{subver}

mv config/cobbler{,_web}.conf .
mv config/{cobblerd,cobblerd_rotate,cobblerd.service,cobbler_bash} .

%build
%py_build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
%py_install

%py_postclean

install -d $RPM_BUILD_ROOT%{_webapps}/%{_webapp}
#cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/apache.conf
#cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/httpd.conf
cp -p cobbler.conf $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/apache.conf
cat cobbler_web.conf >> $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/apache.conf
cp -p $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/{apache,httpd}.conf

install -d $RPM_BUILD_ROOT/var/lib/tftpboot/images
install -d $RPM_BUILD_ROOT/var/spool/koan
install -p cobblerd $RPM_BUILD_ROOT/etc/rc.d/init.d/cobblerd

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add cobblerd
# reserialize and restart
# FIXIT: ?????
#%{_bindir}/cobbler reserialize
%service cobblerd restart

%preun
if [ $1 = 0 ]; then
	/sbin/chkconfig --del cobblerd
	%service cobblerd stop
fi

%if 0
%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}
%endif

%post web
# FIXME: this changes on each upgrade -glen
# Change the SECRET_KEY option in the Django settings.py file
# required for security reasons, should be unique on all systems
RAND_SECRET=$(openssl rand -base64 40 | sed 's/\//\\\//g')
sed -i -e "s/SECRET_KEY = ''/SECRET_KEY = \'$RAND_SECRET\'/" /usr/share/cobbler/web/settings.py

%files
%defattr(644,root,root,755)
%doc AUTHORS CHANGELOG README
%attr(755,root,root) %{_bindir}/cobbler
%attr(755,root,root) %{_bindir}/cobbler-ext-nodes
%attr(755,root,root) %{_bindir}/cobblerd
%attr(755,root,root) %{_sbindir}/tftpd.py*
%{_mandir}/man1/cobbler.1*
%attr(754,root,root) /etc/rc.d/init.d/cobblerd

%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/iso
%dir %{_sysconfdir}/%{name}/ldap
%dir %{_sysconfdir}/%{name}/power
%dir %{_sysconfdir}/%{name}/pxe
%dir %{_sysconfdir}/%{name}/reporting
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/*.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/*.template
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/*/*.template
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/cheetah_macros
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/completions
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/distro_signatures.json
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/import_rsync_whitelist
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/rsync.exclude
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/settings
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/users.digest
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/version

%{py_sitescriptdir}/%{name}
%{py_sitescriptdir}/%{name}*.egg-info

%{_datadir}/augeas/lenses/cobblersettings.aug

%config(noreplace) /var/lib/cobbler
%exclude /var/lib/cobbler/webui_sessions

%{_appdir}
/var/log/cobbler
/var/lib/tftpboot/images

# XXX
%dir /var/www
%dir /var/lib/tftpboot

%files web
%defattr(644,root,root,755)
%doc AUTHORS CHANGELOG README
%dir %attr(750,root,http) %{_webapps}/%{_webapp}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/httpd.conf

%dir %{_datadir}/cobbler
%{_datadir}/cobbler/web
%dir %attr(700,http,root) /var/lib/cobbler/webui_sessions
/var/www/cobbler_webui_content

%files -n koan
%defattr(644,root,root,755)
%doc AUTHORS CHANGELOG README
%attr(755,root,root) %{_bindir}/koan
%attr(755,root,root) %{_bindir}/ovz-install
%attr(755,root,root) %{_bindir}/cobbler-register
%{_mandir}/man1/koan.1*
%{_mandir}/man1/cobbler-register.1*
%{py_sitescriptdir}/koan

%dir /var/spool/koan
%dir /var/lib/koan
%dir /var/lib/koan/config
%dir /var/log/koan
