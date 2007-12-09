Summary:	Boot server configurator
Name:		cobbler
Version:	0.6.4
Release:	0.1
Source0:	http://cobbler.et.redhat.com/download/cobbler-0.6.4.tar.gz
# Source0-md5:	1f46e1860e10b2e250c73ebb2a3d8227
License:	GPL v2+
Group:		Applications/System
Requires:	createrepo
Requires:	httpd
Requires:	mod_python
Requires:	python >= 2.3
Requires:	python-cheetah
Requires:	python-devel
Requires:	rhpl
Requires:	tftp-server
%ifarch i386 i686 x86_64
Requires:	syslinux
%endif
URL:		http://cobbler.et.redhat.com
BuildRequires:	python-cheetah
BuildRequires:	python-devel
#BuildRequires:	redhat-rpm-config
Requires(post):	/sbin/chkconfig
Requires(preun):	/sbin/chkconfig
BuildArch:	noarch
ExcludeArch:	ppc
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Cobbler is a network boot and update server. Cobbler supports PXE,
provisioning virtualized images, and reinstalling existing Linux
machines. The last two modes require a helper tool called 'koan' that
integrates with cobbler. Cobbler's advanced features include importing
distributions from DVDs and rsync mirrors, kickstart templating,
integrated yum mirroring, and built-in DHCP Management. Cobbler has a
Python API for integration with other GPL systems management
applications.

%prep
%setup -q

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
%{__python} setup.py install \
	--optimize=1 \
	--root=$RPM_BUILD_ROOT

%py_postclean

mv $RPM_BUILD_ROOT/etc/{init.d,rc.d/init.d}/cobblerd

%clean
rm -rf $RPM_BUILD_ROOT

%post
cp /var/lib/cobbler/distros*  /var/lib/cobbler/backup 2>/dev/null
cp /var/lib/cobbler/profiles* /var/lib/cobbler/backup 2>/dev/null
cp /var/lib/cobbler/systems*  /var/lib/cobbler/backup 2>/dev/null
cp /var/lib/cobbler/repos*    /var/lib/cobbler/backup 2>/dev/null
%{_bindir}/cobbler reserialize
/sbin/chkconfig --add cobblerd
%service cobblerd restart

%preun
if [ $1 = 0 ]; then
	%service cobblerd stop
	chkconfig --del cobblerd
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS CHANGELOG README
%defattr(755,apache,apache)
%dir /var/www/cgi-bin/cobbler
/var/www/cgi-bin/cobbler/findks.cgi
/var/www/cgi-bin/cobbler/nopxe.cgi
/var/www/cgi-bin/cobbler/webui.cgi
%defattr(660,apache,apache)
%config(noreplace) /var/www/cgi-bin/cobbler/.htaccess
%config(noreplace) /var/www/cgi-bin/cobbler/.htpasswd

%defattr(755,apache,apache)
%dir %{_datadir}/cobbler/webui_templates
%defattr(444,apache,apache)
%{_datadir}/cobbler/webui_templates/*.tmpl

%defattr(4755,apache,apache)
%dir /var/log/cobbler
%dir /var/log/cobbler/kicklog
%dir /var/www/cobbler/
%dir /var/www/cobbler/localmirror
%dir /var/www/cobbler/kickstarts
%dir /var/www/cobbler/kickstarts_sys
%dir /var/www/cobbler/repo_mirror
%dir /var/www/cobbler/repos_profile
%dir /var/www/cobbler/repos_system
%dir /var/www/cobbler/ks_mirror
%dir /var/www/cobbler/ks_mirror/config
%dir /var/www/cobbler/images
%dir /var/www/cobbler/distros
%dir /var/www/cobbler/profiles
%dir /var/www/cobbler/systems
%dir /var/www/cobbler/links
%defattr(755,apache,apache)
%dir /var/www/cobbler/webui
%defattr(444,apache,apache)
/var/www/cobbler/webui/*.css
/var/www/cobbler/webui/*.js
/var/www/cobbler/webui/*.png
/var/www/cobbler/webui/*.html
%defattr(-,root,root)
%dir /tftpboot/pxelinux.cfg
%dir /tftpboot/images
%attr(755,root,root) %{_bindir}/cobbler
%attr(755,root,root) %{_bindir}/cobblerd
%dir %{_sysconfdir}/cobbler
%config(noreplace) %{_sysconfdir}/cobbler/default.ks
%config(noreplace) %{_sysconfdir}/cobbler/kickstart_fc5.ks
%config(noreplace) %{_sysconfdir}/cobbler/kickstart_fc6.ks
%config(noreplace) %{_sysconfdir}/cobbler/kickstart_fc6_domU.ks
%config(noreplace) %{_sysconfdir}/cobbler/dhcp.template
%config(noreplace) %{_sysconfdir}/cobbler/dnsmasq.template
%config(noreplace) %{_sysconfdir}/cobbler/pxedefault.template
%config(noreplace) %{_sysconfdir}/cobbler/pxeprofile.template
%config(noreplace) %{_sysconfdir}/cobbler/pxesystem.template
%config(noreplace) %{_sysconfdir}/cobbler/pxesystem_ia64.template
%config(noreplace) %{_sysconfdir}/cobbler/rsync.exclude
%config(noreplace) /etc/logrotate.d/cobblerd_rotate
%config(noreplace) %{_sysconfdir}/cobbler/modules.conf
%config(noreplace) %{_sysconfdir}/cobbler/webui-cherrypy.cfg
%dir %{py_sitescriptdir}/cobbler
%dir %{py_sitescriptdir}/cobbler/yaml
%dir %{py_sitescriptdir}/cobbler/modules
%dir %{py_sitescriptdir}/cobbler/webui
%{py_sitescriptdir}/cobbler/*.py[co]
%{py_sitescriptdir}/cobbler/yaml/*.py[co]
%{py_sitescriptdir}/cobbler/modules/*.py[co]
%{py_sitescriptdir}/cobbler/webui/*.py[co]
%{_mandir}/man1/cobbler.1*
%attr(754,root,root) /etc/rc.d/init.d/cobblerd
%config(noreplace) %{_sysconfdir}/httpd/conf.d/cobbler.conf
%dir /var/log/cobbler/syslog

%defattr(755,root,root)
%dir /var/lib/cobbler
%dir /var/lib/cobbler/kickstarts/
%dir /var/lib/cobbler/backup/
%dir /var/lib/cobbler/triggers/add/distro/pre
%dir /var/lib/cobbler/triggers/add/distro/post
%dir /var/lib/cobbler/triggers/add/profile/pre
%dir /var/lib/cobbler/triggers/add/profile/post
%dir /var/lib/cobbler/triggers/add/system/pre
%dir /var/lib/cobbler/triggers/add/system/post
%dir /var/lib/cobbler/triggers/add/repo/pre
%dir /var/lib/cobbler/triggers/add/repo/post
%dir /var/lib/cobbler/triggers/delete/distro/pre
%dir /var/lib/cobbler/triggers/delete/distro/post
%dir /var/lib/cobbler/triggers/delete/profile/pre
%dir /var/lib/cobbler/triggers/delete/profile/post
%dir /var/lib/cobbler/triggers/delete/system/pre
%dir /var/lib/cobbler/triggers/delete/system/post
%dir /var/lib/cobbler/triggers/delete/repo/pre
%dir /var/lib/cobbler/triggers/delete/repo/post
%dir /var/lib/cobbler/triggers/sync/pre
%dir /var/lib/cobbler/triggers/sync/post
%dir /var/lib/cobbler/snippets/

%defattr(744,root,root)
%config(noreplace) /var/lib/cobbler/triggers/sync/post/restart-services.trigger

%defattr(664,root,root)
%config(noreplace) /var/lib/cobbler/settings
%config(noreplace) /var/lib/cobbler/snippets/partition_select
/var/lib/cobbler/elilo-3.6-ia64.efi
/var/lib/cobbler/menu.c32
%defattr(660,apache,apache)
%config(noreplace) %{_sysconfdir}/cobbler/auth.conf

%defattr(664,root,root)
%config(noreplace) /var/lib/cobbler/cobbler_hosts
