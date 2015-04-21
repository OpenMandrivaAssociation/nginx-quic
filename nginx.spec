%define nginx_user nginx
%define nginx_group %{nginx_user}
%define nginx_home /var/lib/nginx
%define nginx_home_tmp %{nginx_home}/tmp
%define nginx_logdir /var/log/nginx
%define nginx_confdir %{_sysconfdir}/nginx
%define nginx_datadir %{_datadir}/nginx
%define nginx_webroot %{nginx_datadir}/html

Summary:	Robust, small and high performance HTTP and reverse proxy server
Name:		nginx
Version:	1.8.0
Release:	1
Group:		System/Servers
# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:	BSD
Url:		http://nginx.net/
Source0:	http://nginx.org/download/nginx-%{version}.tar.gz
Source1:	http://nginx.org/download/nginx-%{version}.tar.gz.asc
Source2:	nginx.service
Source3:	nginx.logrotate
Source4:	virtual.conf
Source5:	ssl.conf
Source100:	index.html
Source101:	poweredby.png
Source102:	nginx-logo.png
Source103:	50x.html
Source104:	404.html
BuildRequires:	gd-devel
BuildRequires:	GeoIP-devel
BuildRequires:	perl-devel
BuildRequires:	perl(ExtUtils::Embed)
BuildRequires:	pkgconfig(libpcre)
BuildRequires:	pkgconfig(libxslt)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(zlib)
Requires(pre,postun):	rpm-helper
Requires:	pcre
Requires:	geoip
Requires:	openssl
Provides:	webserver

%description
Nginx [engine x] is an HTTP(S) server, HTTP(S) reverse proxy and IMAP/POP3
proxy server written by Igor Sysoev.

%prep
%setup -q

%build
%setup_compile_flags
./configure \
	--user=%{nginx_user} \
	--group=%{nginx_group} \
	--prefix=%{nginx_datadir} \
	--sbin-path=%{_sbindir}/%{name} \
	--conf-path=%{nginx_confdir}/%{name}.conf \
	--error-log-path=%{nginx_logdir}/error.log \
	--http-log-path=%{nginx_logdir}/access.log \
	--http-client-body-temp-path=%{nginx_home_tmp}/client_body \
	--http-proxy-temp-path=%{nginx_home_tmp}/proxy \
	--http-fastcgi-temp-path=%{nginx_home_tmp}/fastcgi \
	--pid-path=/run/%{name}.pid \
	--lock-path=/var/lock/subsys/%{name} \
	--with-file-aio \
	--with-ipv6 \
	--with-http_ssl_module \
	--with-http_realip_module \
	--with-http_addition_module \
	--with-http_xslt_module \
	--with-http_image_filter_module \
	--with-http_geoip_module \
	--with-http_sub_module \
	--with-http_dav_module \
	--with-http_flv_module \
	--with-http_mp4_module \
	--with-http_gzip_static_module \
	--with-http_random_index_module \
	--with-http_secure_link_module \
	--with-http_degradation_module \
	--with-http_stub_status_module \
	--with-http_perl_module \
	--with-mail \
	--with-mail_ssl_module \
	--with-pcre \
        --with-ld-opt="$RPM_LD_FLAGS -Wl,-E" # so the perl module finds its symbols

# this is only passed to perl module being built and only overrides the
# default '-O' flag which anyways lowers optimizations (which we don't
# want)
%make OPTIMIZE="-fno-PIE"

%install
%makeinstall_std INSTALLDIRS=vendor

find %{buildroot} -type f -name .packlist -exec rm -f {} \;
find %{buildroot} -type f -name perllocal.pod -exec rm -f {} \;
find %{buildroot} -type f -empty -exec rm -f {} \;
find %{buildroot} -type f -exec chmod 0644 {} \;
find %{buildroot} -type f -name '*.so' -exec chmod 0755 {} \;
chmod 0755 %{buildroot}%{_sbindir}/nginx

install -p -D -m 0755 %{SOURCE2} %{buildroot}/lib/systemd/system/nginx.service
install -p -D -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -p -d -m 0755 %{buildroot}%{nginx_confdir}/conf.d
install -p -m 0644 %{SOURCE4} %{SOURCE5} %{buildroot}%{nginx_confdir}/conf.d
install -p -d -m 0755 %{buildroot}%{nginx_home_tmp}
install -p -d -m 0755 %{buildroot}%{nginx_logdir}
install -p -d -m 0755 %{buildroot}%{nginx_webroot}

install -p -m 0644 %{SOURCE100} %{SOURCE101} %{SOURCE102} %{SOURCE103} %{SOURCE104} %{buildroot}%{nginx_webroot}

# add current version
perl -pi -e "s|_VERSION_|%{version}|g" %{buildroot}%{nginx_webroot}/index.html

# convert to UTF-8 all files that give warnings.
for textfile in CHANGES; do
    mv $textfile $textfile.old
    iconv --from-code ISO8859-1 --to-code UTF-8 --output $textfile $textfile.old
    rm -f $textfile.old
done

install -d %{buildroot}%{_mandir}/man8
install -m0644 man/*.8 %{buildroot}%{_mandir}/man8/

%pre
%_pre_useradd %{nginx_user} %{nginx_home} /bin/false

%post
%_post_service %{name}

%preun
%_preun_service %{name}

%postun
%_postun_userdel %{nginx_user}

%files
%doc LICENSE CHANGES README
%{nginx_datadir}/
%{_sbindir}/%{name}
%{_mandir}/man3/%{name}.3pm*
%{_mandir}/man8/*
/lib/systemd/system/nginx.service
%dir %{nginx_confdir}
%dir %{nginx_confdir}/conf.d
%config(noreplace) %{nginx_confdir}/conf.d/*.conf
%config(noreplace) %{nginx_confdir}/win-utf
%config(noreplace) %{nginx_confdir}/%{name}.conf.default
%config(noreplace) %{nginx_confdir}/scgi_params
%config(noreplace) %{nginx_confdir}/scgi_params.default
%config(noreplace) %{nginx_confdir}/fastcgi.conf
%config(noreplace) %{nginx_confdir}/fastcgi.conf.default
%config(noreplace) %{nginx_confdir}/mime.types.default
%config(noreplace) %{nginx_confdir}/fastcgi_params
%config(noreplace) %{nginx_confdir}/fastcgi_params.default
%config(noreplace) %{nginx_confdir}/koi-win
%config(noreplace) %{nginx_confdir}/koi-utf
%config(noreplace) %{nginx_confdir}/%{name}.conf
%config(noreplace) %{nginx_confdir}/mime.types
%config(noreplace) %{nginx_confdir}/uwsgi_params
%config(noreplace) %{nginx_confdir}/uwsgi_params.default
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%dir %{perl_vendorarch}/auto/%{name}
%{perl_vendorarch}/%{name}.pm
%{perl_vendorarch}/auto/%{name}/%{name}.so
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_home}
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_home_tmp}
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_logdir}
