import 'dart:io';

class QrService {
  static Future<String?> getLocalIpAddress() async {
    for (var interface in await NetworkInterface.list()) {
      for (var addr in interface.addresses) {
        if (addr.type == InternetAddressType.IPv4 &&
            !addr.isLoopback &&
            addr.address.startsWith('192.')) {
          return addr.address;
        }
      }
    }
    return null;
  }
}