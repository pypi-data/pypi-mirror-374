const_epilog = "CgpNQU5VQUwKCgoKMS4gR0VUVElORyBTVEFSVEVECi4uIDEuIElOU1RBTExBVElPTgouLi4uLiAxLiBXaW5kb3dzCi4uIDIuIFBPU1QtSU5TVEFMTEFUSU9OCi4uIDMuIFdPUktGTE9XIERFRklOSVRJT04gRk9STUFUCi4uLi4uIDEuIERJUkVDVE9SWSBTVFJVQ1RVUkUKLi4uLi4gMi4gRklMRSBGT1JNQVQKLi4uLi4gMy4gTUlOSU1BTCBFWEFNUExFIGBwbGF5LmpzJwouLiA0LiBDUkVBVEUgTkVXIFdPUktGTE9XCi4uIDUuIFJVTiBUSEUgTkVXIFdPUktGTE9XCi4uIDYuIERJUkVDVE9SWSBgbG9nJyBBRlRFUiBFWEVDVVRJT04KMi4gQ09NTUFORCBSRUZFUkVOQ0UKLi4gMS4gT1ZFUlZJRVcKCgoKCgoxIEdFVFRJTkcgU1RBUlRFRAo9PT09PT09PT09PT09PT09PQoKMS4xIElOU1RBTExBVElPTgp+fn5+fn5+fn5+fn5+fn5+CgoxLjEuMSBXaW5kb3dzCi0tLS0tLS0tLS0tLS0KCiAgSW5zdGFsbCBhIHJlY2VudCBgcHl0aG9uMycgKExUUyByZWxlYXNlcyByZWNvbW1lbmRlZCBmcm9tIHRoZSBvcmlnaW5hbAogIHdlYnNpdGUgPGh0dHBzOi8vd3d3LnB5dGhvbi5vcmcvZG93bmxvYWRzL3dpbmRvd3MvPikgYW5kIHJ1biBgcGlwCiAgaW5zdGFsbCBkY3gnIGFmdGVyd2FyZHMuIE5vdGU6IEl0IGlzIHBvc3NpYmxlIHRvIGhhdmUgeW91ciBweXRob24KICBpbnN0YWxsZWQgaW4geW91ciB1c2VyJ3MgcmVhbG0gd2l0aG91dCB0aGUgbmVlZCBmb3IgYWRtaW5pc3RyYXRvcgogIHByaXZpbGVnZXMuCgogIEluIGEgY29tbWFuZGxpbmUgb3IgdGVybWluYWwgd2hlcmUgeW91IGhhdmUgYWNjZXNzIHRvIGBweXRob24nIHlvdSBjYW4KICB0aGVuIHNpbXBseSBzdGFydCB0aGUgZGN4IGNsaSBieSBydW5uaW5nOgoKICAsLS0tLQogIHwgcHl0aG9uIC1tIGRjeAogIGAtLS0tCgogIG9yIHBlcmhhcHMgd2l0aCBtb3JlIHBhcmFtZXRlcnMgKHNpbWlsYXIgdG8gYC0taGVscCcpOgoKICAsLS0tLQogIHwgcHl0aG9uIC1tIGRjeCAtLWhlbHAKICBgLS0tLQoKCjEuMiBQT1NULUlOU1RBTExBVElPTgp+fn5+fn5+fn5+fn5+fn5+fn5+fn4KCiAgWW91IGhhdmUgKG9idmlvdXNseSkgbWFuYWdlZCB0byBpbnN0YWxsIGBkY3gnIGFscmVhZHkuIEdyZWF0IQoKICBJIHJlY29tbWVuZCBwdXR0aW5nIGEgc3RhcnRlciBiYXNoIHNjcmlwdCBzb21ld2hlcmUgaW4geW91ciBgUEFUSCcsIHNvCiAgeW91IGNhbiBqdXN0IHJ1biBgZGN4JyB3aXRob3V0IHRoZSBweXRob24gdmVudiBpbml0LgoKICBGb3IgZXhhbXBsZSwgeW91IGNvdWxkIGhhdmUgYSBgZGN4JyBmaWxlIGJlbmVhdGggYC91c3IvbG9jYWwvYmluLycKICAoY2hhbmdlIHlvdXIgdmVudiBwYXRoIGlmIG5lY2Vzc2FyeSk6CgogICwtLS0tCiAgfCAjIS9iaW4vYmFzaAogIHwgCiAgfCAuIH4vdmVudi9iaW4vYWN0aXZhdGUKICB8IHB5dGhvbiAtbSBkY3ggIiRAIgogIGAtLS0tCgoKMS4zIFdPUktGTE9XIERFRklOSVRJT04gRk9STUFUCn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fgoKMS4zLjEgRElSRUNUT1JZIFNUUlVDVFVSRQotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCgogIEEgd29ya2Zsb3cgY29uc2lzdHMgKGluIGl0cyBtb3N0IHNpbXBsZSBmb3JtKSBvZiBleGFjdGx5ICpvbmUgZmlsZSoKICBuYW1lZCBgcGxheS5qcycgaW4geW91ciB3b3JraW5nIGRpcmVjdG9yeS4KCgoxLjMuMiBGSUxFIEZPUk1BVAotLS0tLS0tLS0tLS0tLS0tLQoKICBgcGxheS5qcycgaXMgSlNPTiB3aXRoICpvbmx5KiBvbmUgcm9vdCBlbGVtZW50LCBhbiBhcnJheSBgW10nLgoKICBUaGlzIGFycmF5IHN0b3JlcyBhbGwgbGluZWFyIGV4ZWN1dGVkIGBwbGF5X3N0ZXBzJywgd2hpY2ggdGhlbXNlbHZlcwogIGFyZSBhcnJheXMsIGFnYWluLiBUaGV5IHdpbGwgbGF0ZXIgYmUgZXhlY3V0ZWQgaW4tb3JkZXIgZnJvbSB0b3AgdG8KICBib3R0b20uCgogIEJhc2ljIGBwbGF5LmpzJyBzdHJ1Y3R1cmFsIChzdGlsbCBubyBjb250ZW50KToKICAsLS0tLQogIHwgWwogIHwgICBbXSwKICB8ICAgW10sCiAgfCAgIFtdCiAgfCBdCiAgYC0tLS0KCiAgVGhlc2UgKmlubmVyKiBhcnJheXMgKHRoZSBgcGxheV9zdGVwcycpIEFMV0FZUyBjb25zaXN0IG9mIGF0IGxlYXN0IDIKICBjb2x1bW5zLgoKICAxc3QgY29sdW1uOiBgIkpTT04gZW5jb2RlZCBYUGF0aCBTdHJpbmciIHwgbnVsbCcKCiAgMm5kIGNvbHVtbjogYENPTU1BTkQnIG5hbWUsIGFzIFN0cmluZwoKICAzcmQsIDR0aCwgLi4uIGNvbHVtbjogKE9wdGlvbmFsKSBwb3NpdGlvbmFsIHBhcmFtZXRlcnMgZm9yIHRoZSB1c2VkCiAgYENPTU1BTkQnLgoKICBOb3RlOiBBbGwgY29sdW1ucyAqaGF2ZSB0byBiZSogSlNPTiBTdHJpbmdzICh3aXRoIHRoZSBleGNlcHRpb24gb2YgdGhlCiAgMXN0LCB3aGljaCBjYW4gYmUgSlNPTjpudWxsIGluIGNhc2Ugb2YgYSBgQ09NTUFORCcgdGhhdCBkb2VzIG5vdAogIHJlbGF0ZSB0byBhbnkgd2Vic2l0ZS1lbGVtZW50KS4KCgoxLjMuMyBNSU5JTUFMIEVYQU1QTEUgYHBsYXkuanMnCi0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0KCiAgVGhpcyBleGFtcGxlIG1heSBnaXZlIHlvdSBhIGJldHRlciBpZGVhOgoKICBgcGxheS5qcyc6CiAgLC0tLS0KICB8IFsKICB8ICAgW251bGwsICJnZXQiLCAiaHR0cHM6Ly8xMjcuMC4wLjE6ODA4MC8iXSwKICB8ICAgW251bGwsICJoYWx0Il0KICB8IF0KICBgLS0tLQoKICBXaGF0IHlvdSBzZWUgaXMgYW4gZXhhbXBsZSBwbGF5IHdpdGggb25seSAyIGNvbW1hbmQgaW52b2NhdGlvbnMuCgogIFRoZSAxc3QgY29tbWFuZCBpcyBgZ2V0Jywgd2hpY2ggZXF1YWxzIHRvIHR5cGluZyB0aGUgZm9sbG93aW5nIFVSTAogIGludG8geW91ciBhZGRyZXNzIGJhciBhbmQgb3BlbmluZyBpdC4KCiAgVGhlIDJuZCBjb21tYW5kIGtlZXBzIHRoZSBicm93c2VyIG9wZW4gYW5kIHlvdXIgY29tbWFuZGxpbmUgZ29pbmcgaW50bwogIGtpbmQgb2YgYW4gKmludGVyYWN0aXZlKiBtb2RlLiBXaXRob3V0IHRoZSBgaGFsdCcgY29tbWFuZCwgeW91cgogIGJyb3dzZXIgd291bGQgaW1tZWRpYXRlbHkgY2xvc2UgYW5kIGRpc2FwcGVhciBhZnRlciBvcGVuaW5nIHRoZSBVUkwKICBmcm9tIHRoZSBwcmV2aW91cyBzdGVwLiBUbyBza2lwIG91dCB0aGUgaW50ZXJhY3RpdmUgcHJvbXB0LCBqdXN0IHByZXNzCiAgUkVUVVJOLgoKCjEuNCBDUkVBVEUgTkVXIFdPUktGTE9XCn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+CgogIENyZWF0aW5nIGEgbmV3IHdvcmtmbG93L3Rlc3QvcGxheSAod2hhdGV2ZXIgeW91IHdhbnQgdG8gY2FsbCBpdCkKICBzaG91bGQgYWx3YXlzIGhhcHBlbiBpbiBhIG5ldyBlbXB0eSBkaXJlY3RvcnkuCgogIFRvIG1ha2UgaXQgYSBsaXR0bGUgZWFzaWVyIHRvIHN0YXJ0LCB5b3UgY2FuIHJ1bgoKICAsLS0tLQogIHwgbWtkaXIgRVhBTVBMRV9XT1JLRkxPVwogIHwgY2QgRVhBTVBMRV9XT1JLRkxPVwogIHwgZGN4IC0tZ2VuCiAgYC0tLS0KCiAgdG8gY3JlYXRlIGEgc2ltcGxlIHNhbXBsZSBgcGxheS5qcycgZmlsZSBpbiB5b3VyIG5ldyB3b3JraW5nIGRpcmVjdG9yeQogIChoZXJlOiBgRVhBTVBMRV9XT1JLRkxPVycpLgoKCjEuNSBSVU4gVEhFIE5FVyBXT1JLRkxPVwp+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn4KCiAgQmVmb3JlIHlvdSBzdGFydCwgeW91IG5lZWQgdG8ga25vdyB3aGljaCBicm93c2VyIHRvIHVzZS4gSW52b2tpbmcganVzdAogIHBsYWluIGBkY3gnIHdpbGwgdHJ5IGZpcmVmb3guIFlvdSBjYW4gb3ZlcnJpZGUgdGhpcyBiZWhhdmlvdXIgYnkKICBhZGRpbmcgYC0tbG9jYWwtY2hyb21lJyB0byB1c2UgY2hyb21lIGluc3RlYWQuCgogICwtLS0tCiAgfCBjZCBFWEFNUExFX1dPUktGTE9XCiAgfCBkY3ggICAgICAgICAgICAgICAgICAgICMgZm9yIGZpcmVmb3gKICB8IGRjeCAtLWxvY2FsLWNocm9tZSAgICAgIyBmb3IgY2hyb21lCiAgYC0tLS0KCiAgTm90ZTogVGhlIGRpcmVjdG9yeSBgbG9nJyB3aWxsIGJlIGNyZWF0ZWQgZHVyaW5nIHJ1bnRpbWUgLSBhbmQgZGVsZXRlZAogIGF1dG9tYXRpY2FsbHkuIElGIFlPVSBXQU5UIFRPIEtFRVAgSVQgRk9SIElOU1BFQ1RJT04sIEFERCBgLS1sb2cnLgoKCjEuNiBESVJFQ1RPUlkgYGxvZycgQUZURVIgRVhFQ1VUSU9OCn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+CgogIFdBUk5JTkc6IEJ5LWRlZmF1bHQgdGhlIGBsb2cnIGRpcmVjdG9yeSB3aWxsIGFsd2F5cyBiZSByZW1vdmVkCiAgKHJlY3Vyc2l2ZSwgbm8tcHJvbXB0KS4KCgoyIENPTU1BTkQgUkVGRVJFTkNFCj09PT09PT09PT09PT09PT09PT0KCjIuMSBPVkVSVklFVwp+fn5+fn5+fn5+fn4KCiAgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiAgIENvbW1hbmQgICAgICAgICAgICAgRGVzY3JpcHRpb24gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgRXhhbXBsZSAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiAgIGBhdHRyaWJ1dGVfc2V0ZW52JyAgQWRkIHNwZWNpZmllZCBlbGVtZW50J3MgYXR0cmlidXRlIHRvIEVOViAgICAgICAgICAgICAgICAgYFsiaWQ6YnV0dG9uOSIsICJhdHRyaWJ1dGVfc2V0ZW52IiwgImNsYXNzIiwgIkJVVFRPTjlfQ1NTX0NMQVNTRVMiXScgCiAgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiAgIGBiYXNoJyAgICAgICAgICAgICAgRXhlY3V0ZSBhIGJhc2ggY29tbWFuZCB3aXRob3V0IHNpbmdsZSB0aWNzICAgICAgICAgICAgICAgYFtudWxsLCAiYmFzaCIsICJ1cHRpbWUgPiBhaGEiXScgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiAgIGBiYXNoMCcgICAgICAgICAgICAgRXhlY3V0ZSBhIGJhc2ggY29tbWFuZCB3aXRob3V0IHNpbmdsZSB0aWNzIGFuZCByZXR1cm4gMCAgYFtudWxsLCAiYmFzaCIsICJlY2hvIG9rOyBleGl0IDEiXScgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiAgIGBjbGVhcicgICAgICAgICAgICAgRW1wdHkgYDxJTlBVVD4nIG9yIGA8VEVYVEFSRUE+JyAgICAgICAgICAgICAgICAgICAgICAgICAgYFsiaWQ6Zmlyc3RuYW1lIiwgImNsZWFyIl0nICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiAgIGBjbGljaycgICAgICAgICAgICAgQ2xpY2sgb24gZWxlbWVudCBDRU5URVIgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgYFsiaWQ6YnRuLXN1Ym1pdCIsICJjbGljayJdJyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiAgIGBnZXQnICAgICAgICAgICAgICAgT3BlbiBhIFVSTCAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgYFtudWxsLCAiZ2V0IiwgImh0dHBzOi8vd3d3Lmdvb2dsZS5kZSJdJyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiAgIGBoYWx0JyAgICAgICAgICAgICAgRW50ZXIgYnJlYWtwb2ludCAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgYFtudWxsLCAiaGFsdCJdJyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiAgIGBwYXRoJyAgICAgICAgICAgICAgT3BlbiBhIFBBVEgvVVJMIHZvbiB0aGUgc2FtZSBzZXJ2ZXIvaG9zdCAgICAgICAgICAgICAgICAgYFtudWxsLCAicGF0aCIsICIvaW5mby5odG1sIl0nICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiAgIGBzYW0nICAgICAgICAgICAgICAgVXNlIGBzYXkgLXYgU2FtYW50aGEgPC4uLj4nIHRvIHNwZWFrIG9uIG1hY29zICAgICAgICAgICAgYFtudWxsLCAic2FtIiwgImFsbCBzeXN0ZW0gbm9taW5hbCJdJyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiAgIGBzZXRlbnYnICAgICAgICAgICAgQWRkIG9yIGNoYW5nZSBFTlYgcGFyYW1ldGVycyBkdXJpbmcgcnVudGltZSAgICAgICAgICAgICAgYFtudWxsLCAic2V0ZW52IiwgIlBBUkFNX1giLCAiMTIzNCJdJyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiAgIGBzZXR2YWx1ZScgICAgICAgICAgU2V0IGZvcm0gdmFsdWVzIHZpYSBqYXZhc2NyaXB0IGFuZCBub3Qgc2VuZGluZyBrZXlzICAgICAgYFsiaWQ6aW5wdXRmaWVsZDgiLCAic2V0dmFsdWUiLCAiSm9obiBEb2UiXScgICAgICAgICAgICAgICAgICAgICAgICAgCiAgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiAgIGBzbGVlcCcgICAgICAgICAgICAgRnJlZXplIEV4ZWN1dGlvbiBmb3IgU3BlY2lmaWVkIFNlY29uZHMgICAgICAgICAgICAgICAgICAgYFtudWxsLCAic2xlZXAiLCAiOCJdJyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiAgIGB0eXBlJyAgICAgICAgICAgICAgU2VuZCBrZXlzIHRvIGVsZW1lbnQgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgYFsiaWQ6ZnVua3lmaWVsZCIsICJ0eXBlIiwgIkhlbGxvIl0nICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCg=="
const_appversion = "0.75.0"

from pathlib import Path
import base64
import socket
import _thread
import getpass
import os
import sys
import os.path
import logging
import json
import time
import traceback
import subprocess
import datetime
import argparse
import shutil
import getpass
import tabulate
import pathlib
import importlib.util


const_figlet = "IF9fXyAgIF9fX19fICBfXwp8ICAgXCAvIF9fXCBcLyAvCnwgfCkgfCAoX18gPiAgPCAKfF9fXy8gXF9fXy9fL1xfXAogICAgICAgICAgICAgICAgCg=="

import rich
from rich.console import Console

from selenium.webdriver.firefox.options import Options as FFOptions
from selenium.webdriver.chrome.options import Options as CHOptions
from selenium.webdriver.edge.options import Options as EDOptions
from selenium.webdriver.safari.options import Options as SAOptions

from selenium import webdriver

from selenium.webdriver.common.keys import Keys as KEYS
from selenium.webdriver.common.by import By as BY

from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.webdriver.support.ui import Select as SEL
from selenium.webdriver.support import expected_conditions as EC

from urllib.parse import urlparse

import selenium
#from selenium.webdriver.firefox.firefox_profile import FirefoxProfile as FFProfile



epilog = base64.b64decode(const_epilog).decode()
figlet = base64.b64decode(const_figlet).decode()
parser = argparse.ArgumentParser(prog="dcx", epilog=epilog, formatter_class=argparse.RawTextHelpFormatter, description="DAISY CHAINED XPATH processor (v%s) - commandline tool to run JSON defined selenium scripts.\n\n%s\n" % (const_appversion, figlet))
parser.add_argument("--gen", action="store_true", help="Generate a play.js and play.env if non existing and QUIT")
parser.add_argument("--genf", action="store_true", help="Generate a play.js and play.env and run.sh and Makefile")
parser.add_argument("--format", action="store_true", help="Only reformat play.js and exit")
parser.add_argument("--no-dev", action="store_true", help="Disable Developer Tools Auto-Open (Only Firefox)")
parser.add_argument("--no-img", action="store_true", help="Disable screenshots")
parser.add_argument("--log", action="store_true", help="Don't flush directory 'log'")
parser.add_argument("--part", action="store_true", help="After execution of all play.js parts continue play.part.js/play.part mode")
parser.add_argument("--reg", action="store_true", help="Extract reg as reg.zip to the CWD after execution")
parser.add_argument("--local-chrome", action="store_true", help="Use local 'Google Chrome' and not 'Firefox'")
parser.add_argument("--local-edge", action="store_true", help="Use local 'Google Chrome' and not 'Firefox'")
parser.add_argument("--local-safari", action="store_true", help="Use local 'Safari' and not 'Firefox'")
parser.add_argument("--remote-edge", action="store_true", help="Use remote edge")
parser.add_argument("--remote-firefox", action="store_true", help="Use remote firefox")
parser.add_argument("--remote-chrome", action="store_true", help="Use remote chrome")
parser.add_argument("--remote-host", nargs=1, type=str, default=["127.0.0.1"], help="Default is 127.0.0.1")
parser.add_argument("--remote-port", nargs=1, type=int, default=[4444], help="Default is 4444")
parser.add_argument("--hot", nargs=1, type=int, default=[0], help="TCP Port for *hot* step submission via tcp:127.0.0.1:PORT (default is 0=off)")
parser.add_argument("--unzip-profile", nargs=1, type=str, help="PK-Zipped profile contents (flat) -- FIREFOX ONLY")
parser.add_argument("--zip-profile", metavar="ZIP_PREFIX", nargs=1, type=str, help="ZIP Profile after execution (leave out the '.zip' !) -- FIREFOX ONLY")
parser.add_argument("--pre-bash", nargs=1, type=str)
parser.add_argument("--post-bash", nargs=1, type=str)
parser.add_argument("--sec", nargs=1, type=str, metavar="HOST:PORT", help="IP:PORT to sec server (for example'127.0.0.1:8001')")
parser.add_argument("--ffsocks", nargs=1, type=str, metavar="HOST:PORT", help="IP:PORT to socks proxy (for example'127.0.0.1:8000')")
parser.add_argument("--ffhttp", nargs=1, type=str, metavar="HOST:PORT", help="IP:PORT to socks proxy (for example'127.0.0.1:8000')")
parser.add_argument("--ffnoprivacy", action="store_true", help="disable tracking counter measures")
parser.add_argument("--sslkeylogfile", nargs=1, type=str, metavar="FILENAME", help="FILENAME to ssl debugging key logfile")
parser.add_argument("--ff-http2-disable", action="store_true", help="Firefox-Only: Disable http2")
parser.add_argument("--ff-http3-disable", action="store_true", help="Firefox-Only: Disable http3")
parser.add_argument("--ff-webdriver-disable", action="store_true", help="Firefox-Only: Disable http3")
parser.add_argument("--ff-auto-har", action="store_true", help="Firefox-Only: Save HAR files for debugging")
parser.add_argument("--ssl", action="store_true", help="Enforce valid SSL certificates (default without is ignoring SSL warnings, self-signed, ...)")
parser.add_argument("--debug", action="store_true", help="If an error occurs 'go interactive' and keep the window instead of shutting down")
parser.add_argument("--trace", action="store_true", help="If an error occurs also show a ASCII/src traceback")
parser.add_argument("--force", action="store_true", help="Use with caution (for --gen)")
parser.add_argument("--version", action="store_true", help="Show version and exit (no play.js running)")
parser.add_argument("--update", action="store_true", help="Compare with PyPI version and exit (no play.js running)")
parser.add_argument("--headless", action="store_true", help="Run local browsers headless")
parser.add_argument("--ggs", action="store_true", help="Generate Google Search")
parser.add_argument("--report", action="store_true", help="Generate Report")
parser.add_argument("--report-filename", nargs=1, type=str, default=["report.pdf"], metavar="FILENAME.PDF", help="")
parser.add_argument("--plugin", nargs=1, type=str, metavar="PLUGINFILE", help="")

CONSOLE = Console()
from rich.pretty import pprint as PP

args = parser.parse_args()

har_file = "netlog"
har_path = None

global_cookie_snap_index = 0
global_cookie_latest_json_dump_filename = None


class PlayDynamic:

    def __init__(self, static_play, dynamic_src):
        self.static_play_next_index = 0
        self.static_play = static_play

        self.dynamic_src = dynamic_src
        self.mode = "static"

    def set_to_static(self):
        self.mode = "static"

    def set_to_dynamic(self):
        self.mode = "dynamic"

    def __iter__(self):
        return self

    def __next__(self):
        if self.mode == "static":
            if self.static_play_next_index >= len(self.static_play):
                raise StopIteration()
            else:
                self.static_play_next_index+=1
                return self.static_play[self.static_play_next_index-1]
        if self.mode == "dynamic":
            # while self.dynamic_src.empty():
            #     logging.info("Waiting for HOT input...")
            #     time.sleep(1)
            return self.dynamic_src.get(block=True)
            # return global_hot_queue.




report_store = {}

REPORT = {}
REPORT['viewports_in'] = []
REPORT['viewports_out'] = []



if args.version:
    print("dcx-%s(%s)" % (const_appversion, sys.platform))
    sys.exit(0)

if args.update:
    print("Looking up version on pypi.org, ...")
    import requests
    online_version = requests.get('https://pypi.org/pypi/dcx/json').json()["info"]["version"]
    recommend_txt = "nothing to do"
    if online_version != const_appversion:
        recommend_txt = "update to the latest version!"
    print("Latest=%s, installed=%s, %s" % (online_version, const_appversion, recommend_txt))
    sys.exit(0)



#FORMAT = '%(asctime)s+00:00 %(levelname)10s: %(message)-80s    (%(filename)s,%(funcName)s:%(lineno)s)'
FORMAT = '%(asctime)s+00:00 %(levelname)10s: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logging.Formatter.converter = time.gmtime

if args.sslkeylogfile:
    os.environ["SSLKEYLOGFILE"] = args.sslkeylogfile[0]
    logging.info("Environment now with SSLKEYLOGFILE=%s" % os.environ["SSLKEYLOGFILE"])

if args.plugin:
    logging.info("plugin requested")
    logging.info(args.plugin)


# ==================================================================================== special case "gen"
if args.ggs:
    if os.path.isfile("play.js") and args.force == False:
        logging.info("Won't overwrite play.js")
        sys.exit(1)
    else:
        with open('play.js', 'w') as f:
            f.write("""[
    [null, "get", "https://google.de"],
    [null, "sleep", "2"],
    ["/html/body/div[2]/div[3]/div[3]/span/div/div/div/div[3]/div[1]/button[2]/div", "click"],
    ["//textarea[@title=\\"Suche\\"]", "input_type", "such data"],
    ["//textarea[@title=\\"Suche\\"]", "submit"],
    [null, "halt"]                    
]

""")
        logging.info("play.js written successfully, terminating")
        sys.exit(0)

if args.format:
    data = None
    data_s = None
    with open("play.js", "r") as playfile:
        data_s = playfile.read()

    try:
        data = json.loads(data_s)
    except:
        logging.error("Unable to parse play.js, exiting with code 1")
        sys.exit(1)

    data_col0 = []
    data_col1 = []
    data_col_naked = []
    
    width_0 = 0
    width_1 = 0

    for data_item in data:
        
        data_col0.append(json.dumps(data_item[0]))
        if len(data_col0[-1]) > width_0:
            width_0 = len(data_col0[-1])
        
        data_col1.append(json.dumps(data_item[1]))
        if len(data_col1[-1]) > width_1:
            width_1 = len(data_col1[-1])
        
        data_col_naked.append(data_item[2:])
    
    with open("play.js", "w") as formatted_playjs:
        formatted_playjs.write("[\n")
        for data_i in range(0, len(data_col0)):
            data_tail = ""
            if len(data_col_naked[data_i]) > 0:
                data_tail = ", %s " % json.dumps(data_col_naked[data_i])[1:-1]
            formatted_playjs.write("  [ %s%s, %s%s %s]" % (data_col0[data_i], " "*(width_0-len(data_col0[data_i])), data_col1[data_i], " "*(width_1-len(data_col1[data_i])), data_tail))
            if data_i < len(data_col0)-1:
                formatted_playjs.write(",")
            formatted_playjs.write("\n")
        formatted_playjs.write("]\n")
    
    sys.exit(0)


import queue
import threading
global_hot_queue = queue.Queue()

import socketserver
global_hot_port = int(args.hot[0])
print("hot is %d" % global_hot_port)


def killmenow(x):
    x.shutdown()

class HotHandler(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        self.data = self.request.recv(8192).strip()
        if str(self.data.decode()).strip() == "bye":
            logging.info("HOT-THREAD: got bye'd - see you on the other side, slick")
            _thread.start_new_thread(killmenow, (self.server,))
        else:
            global_hot_queue.put(json.loads(""+self.data.decode()))
            #self.request.sendall(self.data)
            return super().handle()


def hot_thread_runner():
    with socketserver.TCPServer(("127.0.0.1", global_hot_port), HotHandler) as server:
        server.serve_forever()


bye_to_hot_counter=0

def bye_to_hot():
    global bye_to_hot_counter
    if global_hot_port > 0 and bye_to_hot_counter ==0:
        logging.info("Sending BYE to HOT thread...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1",global_hot_port))
        s.send('bye'.encode())
        s.close()
        logging.info("Sending BYE to HOT thread... done")
        bye_to_hot_counter+=1


# todo terminate correctly on all exits
hot_thread = None

if __name__ == "__main__" and global_hot_port > 0:
    hot_thread = threading.Thread(target=hot_thread_runner)
    hot_thread.start()
    logging.info("----------------------------------------")
    logging.info("HOT is on and running on port %d" % global_hot_port)
    logging.info("----------------------------------------")
else:
    logging.info("----------------------------------------")
    logging.info("HOT is off")
    logging.info("----------------------------------------")



if args.gen:
    if os.path.isfile("play.js") and args.force == False:
        logging.info("Won't overwrite play.js")
        sys.exit(1)
    else:
        with open('play.js', 'w') as f:
            f.write("""[
    ["//", "========================================================================================================="],
    ["//", "This is an example file - making it hopefully easier to start things for you when you're new to this!"],
    ["//", "========================================================================================================="],
    ["//", "- A play.js file is valid JSON and consists of ONLY ONE singular array (as you can see) with many, many STEPS being arrays for themselves - again"],
    ["//", "- All columns in a STEP array are typed as string! So don't put numbers or booleans in it! (ok, first column can be real null)"],
    ["//", "- If a STEP's first column is a double slash '//' it won't be executed. Just make sure it's still JSON..."],
    ["//", "- 1st column of a step refers to an element with a XPath expression (beware of the escaping, JSON, ...)"],
    ["//", "- 2st column is the actual command you want to execute - followed by any needed columns for parameters"],
    ["//", "- Don't forget - last command must not have a trailing comma, this is JSON..."],
    ["//", "- Your default ENV is prefilled 2 variables: $PWD, $HOME . They can directly be used in 'env' expansion for inputs, ..."],
    ["//", "- Extend four ENV by creating a play.env file. Don't use any ticks after the '=' sign"],
    ["//", ""],
    
    [null, "get", "https://google.de"],
    [null, "path", "/why"],

    [null, "halt"]                    
]
""")
        logging.info("play.js written successfully, terminating")
        sys.exit(0)
# ==================================================================================== special case "gen" end

if args.genf:
    if os.path.isfile("play.js") and args.force == False:
        logging.info("Won't overwrite play.js")
        sys.exit(1)
    else:

        with open('play.js', 'w') as f:
            f.write("""[
    [null, "get", "https://google.de"],
    [null, "halt"]
]
""")
        with open('run.sh', 'w') as f:
            f.write("""#!/bin/bash

rm -fr log
rm -fr _profiles

dcx --no-dev --log --report
""")

        with open('Makefile', 'w') as f:
            f.write("""default:
\tbash run.sh
""")

        if sys.platform.lower().startswith("darwin"):
            subprocess.check_output("chmod a+x run.sh", shell=True)
        logging.info("play.js written successfully, terminating")
        sys.exit(0)
# ==================================================================================== special case "gen" end



if args.pre_bash == None:
    logging.info("no PRE task")
else:
    pre_task = """/bin/bash -c '%s'""" % args.pre_bash[0]
    logging.info("PRE task is %s" % pre_task)
    pre_task_res = subprocess.check_output(pre_task, shell=True, universal_newlines=True)
    logging.info("PRE task output: %s" % pre_task_res)



default_wait = 30

# firefox is default
opts = FFOptions()
if args.no_dev == False:
    opts.add_argument("-devtools")
if args.ssl:
    opts.accept_insecure_certs = False
else:
    opts.accept_insecure_certs = True


if args.ff_auto_har:
    logging.info("FIREFOX: devtools.netmonitor.har.enableAutoExportToFile TRUE")
    opts.set_preference("devtools.netmonitor.har.defaultFileName", har_file)
    opts.set_preference("devtools.netmonitor.har.enableAutoExportToFile", True)
    opts.set_preference("devtools.netmonitor.har.enableAutoExport", True)

if args.ff_webdriver_disable:
    logging.info("FIREFOX: Disabling dom.webdriver.enabled")
    opts.set_preference("dom.webdriver.enabled", False)
    opts.set_preference("useAutomationExtension", False)
    opts.set_preference("marionette.enabled", False)

if args.ff_http2_disable:
    logging.info("FIREFOX: Disabling http2")
    opts.set_preference("network.http.http2.enabled", False)

if args.ff_http3_disable:
    logging.info("FIREFOX: Disabling http3")
    opts.set_preference("network.http.http3.enabled", False)

opts.set_preference("devtools.inspector.showAllAnonymousContent", True)

opts.set_preference('media.mediasource.enabled', False)
opts.set_preference("print.always_print_silent", True)
opts.set_preference("print.printer_Mozilla_Save_to_PDF.print_paper_id", "iso_a4")
opts.set_preference("print.printer_Mozilla_Save_to_PDF.print_paper_height", "297.000")
opts.set_preference("print.printer_Mozilla_Save_to_PDF.print_paper_width", "210.000")
opts.set_preference("print.printer_Mozilla_Save_to_PDF.print_to_file", True)
opts.set_preference("print.printer_Mozilla_Save_to_PDF.print_paper_size_unit", 1)
opts.set_preference("print.printer_Mozilla_Save_to_PDF.print_edge_bottom", 15)
opts.set_preference("print.printer_Mozilla_Save_to_PDF.print_edge_top", 15)
opts.set_preference("print.printer_Mozilla_Save_to_PDF.print_edge_left", 15)
opts.set_preference("print.printer_Mozilla_Save_to_PDF.print_edge_right", 15)
opts.set_preference("print.printer_Mozilla_Save_to_PDF.print_to_filename", "a.pdf")
opts.set_preference("print_printer", "Mozilla Save to PDF")

if args.ffsocks:
    ffsocks_host = args.ffsocks[0].split(":")[0]
    ffsocks_port = int(args.ffsocks[0].split(":")[1])
    opts.set_preference("network.proxy.type", 1)
    opts.set_preference("network.proxy.socks", ffsocks_host)
    opts.set_preference("network.proxy.socks_port", ffsocks_port)

if args.ffhttp:
    ffhttp_host = args.ffhttp[0].split(":")[0]
    ffhttp_port = int(args.ffhttp[0].split(":")[1])
    opts.set_preference("network.proxy.type", 1)
    opts.set_preference("network.proxy.http", ffhttp_host)
    opts.set_preference("network.proxy.http_port", ffhttp_port)
    opts.set_preference("network.proxy.ssl", ffhttp_host)
    opts.set_preference("network.proxy.ssl_port", ffhttp_port)

if args.ffnoprivacy:
    pass
    opts.set_preference("privacy.trackingprotection.pbmode.enabled", False)
    opts.set_preference("privacy.trackingprotection.fingerprinting.enabled", False)
    opts.set_preference("privacy.trackingprotection.emailtracking.pbmode.enabled", False)
    opts.set_preference("privacy.trackingprotection.cryptomining.enabled", False)
    opts.set_preference("privacy.fingerprintingProtection.pbmode", False)

driver_mode = "local-firefox"
driver = None

profiledir_actual = None
abs_profile_dir = os.path.abspath("_profiles/main")
os.makedirs(abs_profile_dir, exist_ok=True)

if args.remote_edge:
    driver_mode = "remote-edge"
    opts = EDOptions()
    opts.add_argument("--inprivate")
    ce = "http://%s:%s/wd/hub" % (args.remote_host[0], str(args.remote_port[0]))
    logging.info("CE=%s" % ce)
    driver = webdriver.Remote(command_executor=ce, options=opts)

if args.remote_firefox:
    driver_mode = "remote-firefox"
    ce = "http://%s:%s/wd/hub" % (args.remote_host[0], str(args.remote_port[0]))
    logging.info("CE=%s" % ce)
    driver = webdriver.Remote(command_executor=ce, options=opts)

if args.local_chrome:
    driver_mode = "local-chrome"
    chrome_options = CHOptions()
    if args.ssl == False:
        chrome_options.add_argument('ignore-certificate-errors')
    driver = webdriver.Chrome(options=chrome_options)

if args.local_edge:
    driver_mode = "local-edge"
    chrome_options = EDOptions()
    driver = webdriver.Edge(options=chrome_options)

if args.local_safari:
    driver_mode = "local-safari"
    chrome_options = SAOptions()
    driver = webdriver.Safari(options=chrome_options)

logbasedir = os.path.join("log", driver_mode, sys.platform.lower() + "-" + datetime.datetime.today().strftime("%Y-%m-%d-%H%M%S"))
os.makedirs(logbasedir, exist_ok=False)

if args.ff_auto_har:
    logging.info("FIREFOX: devtools.netmonitor.har.enableAutoExportToFile TRUE (2)")
    har_logdir = os.path.join(Path.cwd().resolve(), logbasedir)
    har_path = har_logdir
    opts.set_preference("devtools.netmonitor.har.defaultLogDir", har_logdir)
    print("*"*80)
    print(har_logdir)
    print("*"*80)

if driver == None:
    if args.headless:
        opts.add_argument("--headless")
    
    if args.unzip_profile:
        unzip_profile_filename = args.unzip_profile[0]
        logging.info("Unzipping profile %s" % unzip_profile_filename)
        if os.path.isdir(abs_profile_dir):
            shutil.rmtree(abs_profile_dir)
            os.makedirs(abs_profile_dir)
        shutil.unpack_archive(unzip_profile_filename, abs_profile_dir)
        from selenium.webdriver.firefox.firefox_profile import FirefoxProfile as FFProfile
        ffprofile = FFProfile(abs_profile_dir)
        opts.profile = ffprofile
        driver = webdriver.Firefox(options=opts)
    else:
        driver = webdriver.Firefox(options=opts)
    
    profiledir_actual = driver.caps["moz:profile"]
    #shutil.copyfile(os.path.join(profiledir_actual, "cookies.sqlite"), "cookies.sqlite")
    logging.info("Firefox is using a tmp profile from %s" % profiledir_actual)

logging.info("DRIVER-MODE: %s" % driver_mode)



logdir_reg = os.path.join(logbasedir, "reg")
os.makedirs(logdir_reg, exist_ok=False)

logdir_cookies = os.path.join(logbasedir, "cookies")
os.makedirs(logdir_cookies, exist_ok=False)

logdir_urls_pre_after = os.path.join(logbasedir, "urls-pre-after")
os.makedirs(logdir_urls_pre_after, exist_ok=False)

logdir_profiles = os.path.join(logbasedir, "profiles")
os.makedirs(logdir_profiles, exist_ok=False)

logdir_viewport_img = os.path.join(logbasedir, "viewport-img")
os.makedirs(logdir_viewport_img, exist_ok=False)

logdir_full_img = os.path.join(logbasedir, "full-img")
os.makedirs(logdir_full_img, exist_ok=False)


reg_activity_log = {}

def reg_write(k, v):
    if not k in reg_activity_log.keys():
        reg_activity_log[k] = len(reg_activity_log.keys())
    with open(os.path.join(logdir_reg, k), 'w') as f:
        f.write(v)

def reg_read(k):
    with open(os.path.join(logdir_reg, k), 'r') as f:
        return f.read()

def hard_wrap(src: str, cols=64):
    import textwrap
    res = []
    for i in range(0, len(src), cols):
        res.append(src[i:i+cols])
    #res = "\n\n".join(textwrap.wrap(src, 80))
    return "\n".join(res)

def content_provider_facade(src, provider_name=""):
    if "+" in provider_name:
        provider_chain = provider_name.split("+")
        for ci in provider_chain:
            src = content_provider_facade(src, ci)
        return src
    if provider_name == "":
        return src
    if provider_name == "bash":
        return subprocess.check_output("""/bin/bash -c '%s'""" % src, shell=True, universal_newlines=True)
    if provider_name == "env":
        for k in reversed(sorted(envdata.keys())): # to counter shorter prefixes
            kstring = "$" + k
            src = src.replace(kstring, envdata[k])
        return src
    if provider_name == "sec":
        for k in reversed(sorted(secdata.keys())): # to counter shorter prefixes
            kstring = "$" + k
            src = src.replace(kstring, secdata[k])
        return src


def get_all_a_href(min_slashes=0, beneath=None):
    all_href={}
    all_a = driver.find_elements(BY.XPATH, "//a")
    if beneath is not None:
        all_a = beneath.find_elements(BY.XPATH, ".//a")
    for a in all_a:
        href = a.get_attribute("href")
        ac = ['_' for x in href if x=="/"]
        if len(ac) >= min_slashes:
            all_href[href] = True
    return sorted(list(all_href.keys()))

play = None

def process_report(logbasedir_):
    if args.reg:
        if os.path.exists("reg.zip"):
            os.unlink("reg.zip")
        shutil.make_archive("reg", "zip", os.path.join(logbasedir_, "reg"))

    if args.report:
        logging.info("Building report...")
        report_filename = os.path.join(logbasedir, args.report_filename[0])
        import turbowriter
        import PIL.Image
        
        pdf = turbowriter.DINA3()
        the_page = 0
        the_page += 1

        pdf.page(the_page).text(1,15,"            *** THIS DOCUMENT MAY CONTAIN CONFIDENTIAL DATA *** DO !!! NOT !!! TRANSMIT WITHOUT ENCRYPTION ***")
        pdf.page(the_page).text(2,15,"                                        H A N D L E   W I T H   C A U T I O N")
        pdf.page(the_page).text(4,15,"                                      This document uses a [DIN A3] page layout")
        import textwrap
        NCOLS=122
        #pdf.page(the_page).text(10,15,"*"*NCOLS)
        
        centerline = "PLAY: " + envdata["PWD"]
        pdf.page(the_page).text(20+3*0,15,centerline.center(NCOLS))
        
        centerline = "MODE: " + driver_mode
        pdf.page(the_page).text(20+3*1,15,centerline.center(NCOLS))

        dcxver = "unknown"
        try:
            from importlib.metadata import version as GET_PIPPED_VERSION
            dcxver = GET_PIPPED_VERSION("dcx")
        except:
            pass

        centerline = "SYS: " + "python=%d.%d / engine=%s / os=%s / host=%s / user=%s" % (sys.version_info.major, sys.version_info.minor, dcxver, sys.platform, socket.gethostname(), getpass.getuser())
        pdf.page(the_page).text(20+3*2,15,centerline.center(NCOLS))

        centerline = "CMDLINE: " + " ".join(sys.argv[1:])
        pdf.page(the_page).text(20+3*3,15,centerline.center(NCOLS))
        
        centerline = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S +0000")
        pdf.page(the_page).text(20+3*5,15,centerline.center(NCOLS))
        
        user_id_from_os = -1
        # win doesn't have this
        if hasattr(os, "getuid") and callable(getattr(os, "getuid")):
            user_id_from_os = os.getuid()

        testdata = tabulate.tabulate(tabular_data=[
            ["",""],
            ["Execution Result    : ", "[x] OK        [ ] Failed        [ ] Failed on internal error"],
            ["",""],
            ["Execution DURATION  : ", "8sec (=0d 0h 0min 8sec)"],
            ["Execution START     : ", "10:30"],
            ["Execution STOP      : ", "10:31"],
            ["",""],
            ["Python / Platform   : ", "%d.%d / %s" % (sys.version_info.major, sys.version_info.minor, sys.platform)],
            ["Hostname            : ", socket.gethostname()],
            ["User (UID)          : ", "%s (%d)" % (getpass.getuser(), user_id_from_os)],
            ["Browser Mode        : ", driver_mode],
            ["Test Engine         : ", "dcx-" + const_appversion],
            ["",""],
            ["Directory           : ", envdata["PWD"]],
                                                   ], headers=["S U M M A R Y", ""])
        # blank first page pdf.page(the_page).text(12,20,testdata)

        table_envdata = [["", ""]]

        for ek in envdata.keys():
            table_envdata.append([ek, envdata[ek]])

        testdata = tabulate.tabulate(tabular_data=table_envdata, headers=["E N V", ""])
        # blank first page pdf.page(the_page).text(52,20,testdata)


        i=5
        the_page += 1
        
        active_report_i = 0 # sub the comments...

        for report_i in range(0, len(play)):
            screenshot_w_default_mm = 220

            report_play_part = play[report_i]
            report_current_target = report_play_part[0]
            if report_current_target == "//":
                continue
            else:
                active_report_i += 1
            
            # page header ####################################################################################
            #pdf.page(the_page).text(5,5, "_"*55 + " [ COMMAND ] " + "_"*55)

            pdf_command = ""
            if len(report_play_part) >= 2:
                pdf_command = report_play_part[1]

            pdf.page(the_page).text( 2,10, "TARGET                     :  " + str(report_play_part[0]))
            pdf.page(the_page).text( 3,10, "COMMAND                    :  " + str(pdf_command))
            pdf.page(the_page).text( 4,10, "PARAMS                     :  ")
            param_human = []
            for report_param in report_play_part[2:]:
                param_human.append("(%d) '%s'" % (len(param_human)+1, report_param))
            param_human = ", ".join(param_human)
            pdf.page(the_page).text( 5,10, "  " + param_human)
            
            pdf.page(the_page).text( 6,10, "STEP (1..)                 :  %d" % active_report_i)
            # pdf.page(the_page).text( 7,10, "STEP ENTERED               :  -")
            # pdf.page(the_page).text( 8,10, "STEP LEFT                  :  -")
            # pdf.page(the_page).text( 9,10, "STEP DURATION              :  -")
            # pdf.page(the_page).text(10,10, "TOTAL DURATION (incl this) :  -")
            
            url_pre = "n/a"
            url_after = "n/a"
            try:
                urls_pre_filename = os.path.join(logdir_urls_pre_after, 'urls-%08d-pre' % active_report_i)
                urls_after_filename = os.path.join(logdir_urls_pre_after, 'urls-%08d-after' % active_report_i)
                with open(urls_pre_filename, 'r') as urls_pre_filename_:
                    url_pre = urls_pre_filename_.read().split("\n")[0].strip()
                with open(urls_after_filename, 'r') as urls_after_filename_:
                    url_after = urls_after_filename_.read().split("\n")[0].strip()

            except:
                pass

            pdf.page(the_page).text(12,2, "> %s" % url_pre)
            pdf.page(the_page).text(13,2, "< %s" % url_after)
            
            pdf.page(the_page).text(30-4,1, "\n".join("before"))
            pdf.page(the_page).text(20-4,4, "\n".join("|"*40))
            #pdf.page(the_page).text(20-4,5, "\n".join("|"*40))
            
            pdf.page(the_page).text(30-4,135, "\n".join("before"))
            #pdf.page(the_page).text(20-4,4+127, "\n".join("|"*40))
            pdf.page(the_page).text(20-4,5+127, "\n".join("|"*40))
            
            pdf.page(the_page).text(72,1, "\n".join("after"))
            pdf.page(the_page).text(62,4, "\n".join("|"*40))
            #pdf.page(the_page).text(60,5, "\n".join("|"*40))

            pdf.page(the_page).text(72,135, "\n".join("after"))
            #pdf.page(the_page).text(60,4+127, "\n".join("|"*40))
            pdf.page(the_page).text(62,5+127, "\n".join("|"*40))

            pdf.page(the_page).text(15,10, "_"*52 + " [ before  ] " + "_"*52)

            pdf.page(the_page).text(61,10, "_"*52 + " [ after   ] " + "_"*52)

            # IN screenshot###################################################################################
            try:
                png = REPORT['viewports_in'][report_i]
                jpg = "%s.jpg" % png
                png_ = PIL.Image.open(png)
                jpg_ = png_.convert("RGB")
                jpg_.save(jpg)
                jpg_width, jpg_height = jpg_.size
                jpg_landscape = jpg_width >= jpg_height
                image_params = []
                if jpg_landscape:
                    # bring to maximal width (DIN A3 Port = 250mm)
                    jpg_ratio = float(jpg_width) / float(jpg_height) # 1.XXXX
                    calclulated_height = int(float(screenshot_w_default_mm) / jpg_ratio)
                    image_params = [25, 185, screenshot_w_default_mm, calclulated_height, jpg]
                else:
                    #TODO: porttrait mode
                    pass
                pdf.page(the_page).image_manual_mm(*image_params)
            except IndexError:
                pass

            # OUT screenshot##################################################################################
            
            # screenshot maybe missing

            try:
                png = REPORT['viewports_out'][report_i]
                jpg = "%s.jpg" % png
                png_ = PIL.Image.open(png)
                jpg_ = png_.convert("RGB")
                jpg_.save(jpg)
                jpg_width, jpg_height = jpg_.size
                jpg_landscape = jpg_width >= jpg_height
                image_params = []
                if jpg_landscape:
                    # bring to maximal width (DIN A3 Port = 250mm)
                    jpg_ratio = float(jpg_width) / float(jpg_height) # 1.XXXX
                    calclulated_height = int(float(screenshot_w_default_mm) / jpg_ratio)
                    image_params = [25, 5, screenshot_w_default_mm, calclulated_height, jpg]
                else:
                    #TODO: porttrait mode
                    pass
                pdf.page(the_page).image_manual_mm(*image_params)
            except IndexError:
                pass

            the_page += 1
            i+=1

        pdf.page(the_page).text(1, 10, "END OF EXECUTION")
        the_page += 1

        pdf.page(the_page).text(1, 10, "[APPENDIX]")
        the_page += 1

        # pdf.page(the_page).text(1, 10, "[APPENDIX] - [COOKIES] - [OVERVIEW] ()")

        cookie_table = []
        cookie_table_cookie = {}
        cookie_table_sorter = {}

        if global_cookie_latest_json_dump_filename != None:
            exit_cookies = json.loads(open(global_cookie_latest_json_dump_filename, "r").read())
            cookie_counter = 0
            cookie_value_accu = 0
            for exit_cookie in exit_cookies:
                cookie_counter += 1
                cookie_value_accu += len(exit_cookie["value"])
                import uuid
                tmp_key = str(exit_cookie["name"]).upper() + "-" + str(uuid.uuid4())
                cookie_table_sorter[tmp_key] = [exit_cookie["name"] + " (%d)" % cookie_counter, "%s - %s - %d" % ('HTTP' if exit_cookie["httpOnly"] == True else '____', 'SEC' if exit_cookie["secure"] == True else '___',len(exit_cookie["value"])),exit_cookie["domain"],exit_cookie["path"]]
                import copy
                cookie_table_cookie[tmp_key] = copy.deepcopy(exit_cookie)
                #cookie_table.append([exit_cookie["name"] + " (%d)" % cookie_counter, "%s - %s - %d" % ('HTTP' if exit_cookie["httpOnly"] == True else '____', 'SEC' if exit_cookie["secure"] == True else '___',len(exit_cookie["value"])),exit_cookie["domain"],exit_cookie["path"]])

            for cookie_sorter_key in list(sorted(cookie_table_sorter.keys())):
                cookie_table.append(cookie_table_sorter[cookie_sorter_key])


            #pdf.page(the_page).text(3, 10, "\n".join(cookie_table))
            cookie_table_txt = tabulate.tabulate(tabular_data=cookie_table, headers=["NAME", "HTTP - SEC - Value-Length", "Domain", "Path"], tablefmt="grid")
            
            pdf.page(the_page).text(1, 10, "[APPENDIX] - [COOKIES] - [OVERVIEW] (%d)" % cookie_value_accu)
            pdf.page(the_page).text(3, 2, cookie_table_txt)

        the_page += 1

        for cookie_sorter_key in list(sorted(cookie_table_sorter.keys())):
            the_cookie = cookie_table_cookie[cookie_sorter_key]
            pdf.page(the_page).text(1, 10, "[APPENDIX] - [COOKIES] - [%s]" % the_cookie["name"])
            pdf.page(the_page).text(3, 10, hard_wrap(the_cookie["value"]))
            the_page += 1

        pdf.page(the_page).text(1, 10, "EOF")
        the_page += 1


        pdf.page_numbers11()
        pdf.build(report_filename)
        shutil.copyfile(report_filename, os.path.join(".", args.report_filename[0]))
        logging.info("Building report... Done")


def break_handler(data):
    if data == "?":
        print("")
        print("HELP")
        print("")
    if data == "c":
        for cookie in driver.get_cookies():
            print(cookie)
    if data == "d":
        b = driver.find_element(BY.XPATH, "//body")
        with open("BODY", "w") as bf:
            bf.write(b.get_attribute("innerHTML"))

        # with open("A", "w") as af:
        #     af.write("\n".join(get_all_a_href(5)))


        pass
        #debug dev
        # vids = driver.find_elements(BY.XPATH, "//video/source")
        # for v in vids:
        #     print(v)
        #     print("_%s_" % v.get_attribute("src"))
        #     print("===")
    if data == "h":
        print("href=%s" % driver.execute_script('return location.href;'))
    if data == "r":
        print("Dumping registry: %d entries" % len(reg_activity_log))
        for x in reg_activity_log.keys():
            print("  %s = %s" % (x, reg_read(x)))
    if data == "q":
        print("QUIT")
        if args.zip_profile:
            postrun_profile_zip = args.zip_profile[0]
            shutil.make_archive(postrun_profile_zip, "zip", profiledir_actual)

        process_report(logbasedir)

        driver.quit()
        bye_to_hot()
        if args.log == False:
            shutil.rmtree(logbasedir)
        sys.exit(0)

# src=["b", "n"], l=2, idx=1
def expand_column(src, idx):
    content = src[idx]
    if idx+1 <= len(src)-1:
        content = content_provider_facade(content, src[idx+1])
    return content


envdata = {}
envdata["HOME"] = os.getenv("HOME")
if envdata["HOME"] == None:
    envdata["HOME"] = str(pathlib.Path.home())
    
envdata["PWD"] = os.getenv("PWD")
if envdata["PWD"] == None:
    envdata["PWD"] = os.getcwd()

secdata = {}
sec_hack = None
sec_server = None


if args.sec:
    sec_server = args.sec[0]
    if sec_server.startswith("file:"):
        sec_hack = sec_server.split(":")[1] # other ':'s?
        seclines = [l.strip() for l in open(sec_hack, "r").read().strip().split() if l.strip() != ""]
        for l in seclines:
            epos=l.find("=")
            k = l[0:epos]
            v = l[epos+1:]
            secdata[k]=v


def interactive_break():
    while True:
        print("*** DEBUG HALT ***")
        break_input = input("Press RETURN (no input) to continue (leave DEBUG HALT)... $ ")
        if break_input == "":
            break
        else:
            break_handler(break_input)


if os.path.isfile("play.js"):

    if os.path.isfile("play.env"):
        envlines = [l.strip() for l in open("play.env", "r").read().strip().split() if l.strip() != ""]
        for l in envlines:
            epos=l.find("=")
            k = l[0:epos]
            v = l[epos+1:]
            envdata[k]=v

        # initialize temporary secret retrieval
        if sec_hack == None:
            for k in envdata.keys():
                if k.startswith("SECRET_"):
                    logging.info("SECRET requested with id %s" % k)
                    #todo: implement secret retrieval
                    secdata[k + "_USERNAME"] = "x"
                    secdata[k + "_PASSWORD"] = "x"
                    secdata[k + "_URI"] = "x"
                    secdata[k + "_ID"] = "x"
                    secdata[k + "_COMMENT"] = "x"

    logging.info("Dumping ENV:")
    for k in envdata.keys():
        logging.info("-> ENV(%s) = %s" % (k, envdata[k]))
    logging.info("Dumping ENV Done")

    play_raw = ""
    with open("play.js", "r") as playfile:
        play_raw = playfile.read()

    try:
        play = json.loads(play_raw)
    except:
        logging.error("Unable to parse play.js, exiting with code 1")
        play_raw_lines = [ l__.strip() for l__ in play_raw.replace("\r", "").split("\n") if l__.strip() != ""]
        if len(play_raw_lines) > 3:
            play_raw_items = play_raw_lines[1:-2]
            for l__ in play_raw_items:
                if not l__.endswith(","):
                    logging.warning("Possible missing ',' and line-end for: %s" % l__)
        sys.exit(1)

    play_part_i = 0
    wait_lel_clickable = False

    play_iter = None
    if global_hot_port > 0:
        play_iter = PlayDynamic(static_play=play, dynamic_src=global_hot_queue)
    else:
        play_iter = play

    for play_part in play_iter:
        PP(play_part)
        ppl = len(play_part) # play part length
        play_part_i+=1

        logging.info("PLAY::EXECUTE(%d) %s" % (play_part_i, str(play_part)))

        try:

            logdir_part = os.path.join(logbasedir, "parts", "part-%04d" % play_part_i)
            os.makedirs(logdir_part, exist_ok=False)

            #pre tasks

            urls_pre_filename = os.path.join(logdir_urls_pre_after, 'urls-%08d-pre' % play_part_i)
            with open(urls_pre_filename, 'w') as urls_pre_filename_:
                urls_pre_filename_.write("")
            try:
                with open(urls_pre_filename, 'w') as urls_pre_filename_:
                    urls_pre_filename_.write(driver.current_url)
            except:
                pass


            viewport_png_in = os.path.join(logdir_viewport_img, 'part-%08d-in.png' % play_part_i)
            if args.no_img == False:
                driver.save_screenshot(viewport_png_in)
                REPORT['viewports_in'].append(viewport_png_in)

            if args.no_img == False:
                if callable(hasattr(driver, 'save_full_page_screenshot')): # only firefox has it
                    full_png_in = os.path.join(logdir_full_img, 'part-%08d-in.png' % play_part_i)
                    driver.save_full_page_screenshot(full_png_in)

            unknown_command = True
            if play_part[0] == None:
                
                if play_part[1] == "hot": ###ntcommand
                    play_iter.set_to_dynamic()
                    unknown_command=False

                if play_part[1] == "unhot": ###ntcommand
                    play_iter.set_to_static()
                    unknown_command=False

                if play_part[1] == "input_env": ###ntcommand
                    input_env_var = play_part[2]
                    input_env_caption = expand_column(play_part, 3)
                    input_env_data = input(input_env_caption + ": ")
                    envdata[input_env_var] = input_env_data.strip().split("\n")[0].strip()
                    unknown_command=False

                if play_part[1] == "save_profile": ###ntcommand
                    save_profile_name = play_part[2]
                    profiledir_actual = driver.caps["moz:profile"]
                    shutil.make_archive(save_profile_name, "zip", profiledir_actual)
                    #shutil.copyfile(os.path.join(profiledir_actual, "cookies.sqlite"), "cookies.sqlite")
                    #print(profiledir_actual)
                    unknown_command=False

                if play_part[1] == "ready": ###ntcommand
                    # wait for document.readyState === 'complete'
                    ready_ttl_secs = default_wait

                    logging.info("Waiting for document.readyState to be complete (max wait secs = %d)..." % ready_ttl_secs)

                    while ready_ttl_secs > 0:
                        the_document_readystate = driver.execute_script("return document.readyState === 'complete';")
                        if type(the_document_readystate) is bool:
                            if the_document_readystate == True:
                                logging.info("READY")
                                break
                            else:
                                ready_ttl_secs -= 1
                                logging.info("Not yet ready, waiting 1 sec before re-check...")
                                time.sleep(1)
                        else:
                            raise Exception("Error, document.readyState === 'complete' didn't return bool.")
                    
                    if ready_ttl_secs <= 0:                    
                        raise Exception("document.readyState never reached complete state")
                    
                    unknown_command=False
                
                if play_part[1] == "save_cookies": ###ntcommand
                    cookies_dump_name = play_part[2]
                    pwd_cookies = None
                    try:
                        pwd_cookies = play_part[3]
                    except:
                        pwd_cookies = None
                    cookie_filename = os.path.join(logdir_cookies, cookies_dump_name)
                    cookie_data = driver.get_cookies()
                    with open(cookie_filename, 'w') as cookiefile:
                        cookiefile.write(json.dumps(cookie_data, indent=4))
                    if pwd_cookies != None:
                        with open(pwd_cookies, 'w') as cookiefile:
                            cookiefile.write(json.dumps(cookie_data, indent=4))
                    cookie_data = None
                    unknown_command=False

                # if play_part[1] == "load_cookies": ###ntcommand
                #     cookies_dump_name = play_part[2]
                #     cookie_filename = os.path.join(logdir_cookies, cookies_dump_name)
                #     #driver.execute_script("window.scrollBy(0,%d);" % int(down_px))
                #     unknown_command=False

                if play_part[1] == "init_cookies": ###ntcommand
                    pwd_cookies = play_part[2]
                    cookie_data = None
                    driver.delete_all_cookies()
                    with open(pwd_cookies, 'r') as cookiefile:
                        cookie_data = json.loads(cookiefile.read())
                        for cookie_item in cookie_data:
                            driver.manage().add_cookie(cookie_item)
                    unknown_command=False

                if play_part[1] == "down": ###ntcommand
                    down_px = play_part[2]
                    driver.execute_script("window.scrollBy(0,%d);" % int(down_px))
                    unknown_command=False

                if play_part[1] == "pdf": ###ntcommand
                    pdf_filename = play_part[2]
                    driver.execute_script("window.print();")
                    unknown_command=False

                if play_part[1] == "clickjs": ###ntcommand
                    element_id = play_part[2]
                    driver.execute_script("console.log('click');")
                    driver.execute_script("console.log(document.getElementById(arguments[0]));")
                    driver.execute_script("document.getElementById(arguments[0]).click();", element_id)
                    unknown_command=False

                if play_part[1] == "bash": ###ntcommand
                    bash_command = expand_column(play_part, 2)
                    logging.info("Will execute bash with '%s'" % bash_command)
                    bash_o = subprocess.check_output("""/bin/bash -c '%s'""" % bash_command, shell=True, universal_newlines=True)
                    unknown_command=False

                if play_part[1] == "bash0": ###ntcommand
                    bash_command = expand_column(play_part, 2)
                    logging.info("Will execute bash with '%s'" % bash_command)
                    bash_o = subprocess.check_output("""/bin/bash -c '%s; exit 0'""" % bash_command, shell=True, universal_newlines=True)
                    unknown_command=False

                if play_part[1] == "conf": ###ntcommand
                    conf_k = play_part[2]
                    conf_v = play_part[3]
                    conf_ok = False
                    
                    if conf_k == "default_wait":
                        default_wait = int(conf_v)
                        logging.info("reconfig: default_wait set to %d seconds" % default_wait)
                        conf_ok=True
                        unknown_command=False
                    
                    if conf_ok == False:
                        raise Exception("Unable to reconfigure with - %s" % str(play_part))

                if play_part[1] == "get": ###ntcommand
                    url_for_get = expand_column(play_part, 2)
                    driver.get(url_for_get)
                    unknown_command=False

                if play_part[1] == "setenv": ###ntcommand
                    env_key = play_part[2]
                    env_value = expand_column(play_part, 3)
                    envdata[env_key] = env_value
                    unknown_command=False

                if play_part[1] == "waitfor": ###ntcommand
                    waitfor_type = play_part[2]
                    waitfor_value = expand_column(play_part, 3)
                    if waitfor_type == "file":
                        logging.info("Waiting for file to exist: [%s]" % waitfor_value)
                        while not os.path.isfile(waitfor_value):
                            time.sleep(1)
                        logging.info("Found [%s]" % waitfor_value)
                    unknown_command=False

                if play_part[1] == "sam": ###ntcommand
                    sentence = play_part[2]
                    subprocess.call("""/bin/bash -c "say -v Samantha '%s'; exit 0" """ % sentence, shell=True)
                    unknown_command=False

                if play_part[1] == "msg": ###ntcommand
                    info_text = play_part[2]
                    msg_text = expand_column(play_part, 3)
                    print("-"*64)
                    print("")
                    print(">>>>>>>> MSG: %s <<<<<<<<" % info_text)
                    print("")
                    print("%s" % msg_text)
                    print("")
                    print("-"*64)
                    unknown_command=False

                if play_part[1] == "copy": ###ntcommand
                    info_text = play_part[2]
                    msg_text = expand_column(play_part, 3)
                    subprocess.run("pbcopy", input=msg_text.encode("utf-8"))
                    logging.info("COPIED TO PASTEBIN")
                    print("-"*64)
                    print("")
                    print(">>>>>>>> MSG: %s <<<<<<<<" % info_text)
                    print("")
                    print("%s" % msg_text)
                    print("")
                    print("-"*64)
                    unknown_command=False

                if play_part[1] == "copy1s": ###ntcommand
                    info_text = play_part[2]
                    msg_text = expand_column(play_part, 3)
                    subprocess.run("pbcopy", input=msg_text.split("\n")[0].strip().encode("utf-8"))
                    logging.info("COPIED TO PASTEBIN")
                    print("-"*64)
                    print("")
                    print(">>>>>>>> MSG: %s <<<<<<<<" % info_text)
                    print("")
                    print("%s" % msg_text)
                    print("")
                    print("-"*64)
                    unknown_command=False

                if play_part[1] == "max": ###ntcommand
                    driver.maximize_window()
                    time.sleep(1)
                    unknown_command=False

                if play_part[1] == "meta": ###ntcommand
                    play_meta_key = play_part[2]
                    play_meta_value = play_part[3]
                    #TODO: Do something
                    unknown_command=False

                if play_part[1] == "window": ###ntcommand
                    window_spec = play_part[2]
                    if window_spec == "max":
                        driver.maximize_window()
                        unknown_command=False
                    if window_spec == "vga":
                        driver.set_window_size(640, 480)
                        unknown_command=False
                    if window_spec == "svga":
                        driver.set_window_size(800, 600)
                        unknown_command=False
                    if window_spec == "xga":
                        driver.set_window_size(1024, 768)
                        unknown_command=False
                    if window_spec == "720p":
                        driver.set_window_size(1280, 720)
                        unknown_command=False
                    if window_spec == "1080p":
                        driver.set_window_size(1920, 1080)
                        unknown_command=False
                    if window_spec == "sxga":
                        driver.set_window_size(1280, 1024)
                        unknown_command=False
                    if window_spec == "wuxga":
                        driver.set_window_size(1920, 1200)
                        unknown_command=False
                    if window_spec == "iphone12":
                        driver.set_window_size(390, 844)
                        unknown_command=False
                    time.sleep(1)

                if play_part[1] == "path": ###ntcommand
                    urlpart_for_get = expand_column(play_part, 2)
                    url_actual = driver.execute_script('return location.href;').strip().split("\n")[0].strip()
                    url_data = urlparse(url_actual)
                    url_target = url_data.scheme + "://" + url_data.netloc + urlpart_for_get
                    driver.get(url_target)
                    unknown_command=False

                if play_part[1] == "sleep":###ntcommand
                    if ppl == 2:
                        time.sleep(1)
                    else:
                        time.sleep(float(play_part[2]))
                    unknown_command=False

                if play_part[1] == "halt":###ntcommand
                    interactive_break()
                    unknown_command=False

                if play_part[1] == "clickable":###ntcommand
                    wait_lel_clickable = True
                    unknown_command=False

                if play_part[1] == "click_any_const":###ntcommand
                    any_consts = [x for x in play_part[2:]]
                    constructed_xpath = "//*[" + " or ".join(["text()=\"%s\"" % x for x in any_consts]) + "]"
                    any_lel = WDW(driver=driver, timeout=default_wait).until(lambda x: x.find_elements(BY.XPATH, constructed_xpath))
                    if any_lel is None or len(any_lel) == 0:
                        raise Exception("could not click one of %s" % str(any_consts))
                    #driver.execute_script("arguments[0].scrollIntoView(true);", any_lel[0])
                    any_lel[0].click()
                    unknown_command=False

                # if play_part[1] == "by_css":###ntcommand
                #     shadow_target_spec = play_part[2]
                #     shadow_lel_concrete = WDW(driver=driver, timeout=default_wait).until(lambda x: x.find_elements(BY.CSS_SELECTOR, shadow_target_spec))
                #     shadow_lel_concrete[0].click()
                #     unknown_command=False

                if play_part[1] == "click_any_const_contains":###ntcommand
                    any_consts = [x for x in play_part[2:]]
                    constructed_xpath = "//*[" + " or ".join(["contains(., \"%s\")" % x for x in any_consts]) + "]"
                    any_lel = WDW(driver=driver, timeout=default_wait).until(lambda x: x.find_elements(BY.XPATH, constructed_xpath))
                    if any_lel is None or len(any_lel) == 0:
                        raise Exception("could not click one of %s" % str(any_consts))
                    #driver.execute_script("arguments[0].scrollIntoView(true);", any_lel[0])
                    any_lel[0].click()
                    unknown_command=False

                if play_part[1] == "click_any_const_startswith":###ntcommand
                    any_consts = [x for x in play_part[2:]]
                    constructed_xpath = "//*[" + " or ".join(["starts-with(., \"%s\")" % x for x in any_consts]) + "]"
                    logging.info(constructed_xpath)
                    any_lel = WDW(driver=driver, timeout=default_wait).until(lambda x: x.find_elements(BY.XPATH, constructed_xpath))
                    if any_lel is None or len(any_lel) == 0:
                        raise Exception("could not click one of %s" % str(any_consts))
                    any_lel[0].click()
                    unknown_command=False

                if play_part[1] == "js64str":###ntcommand
                    varname = play_part[2]
                    code_plain = base64.b64decode(play_part[3]).decode("utf-8")
                    res = str(driver.execute_script(code_plain))
                    reg_write(varname, res)
                    unknown_command=False

                if play_part[1] == "js64":###ntcommand
                    code_plain = base64.b64decode(play_part[2]).decode("utf-8")
                    driver.execute_script(code_plain)
                    unknown_command=False

                if play_part[1] == "reg_href":###ntcommand
                    varname = play_part[2]
                    newdata = driver.execute_script('return location.href;').strip()
                    olddata=""
                    if "+" in varname:
                        # append mode
                        varname = varname.replace("+", "")
                        olddata = reg_read(varname)
                    reg_write(varname, olddata + newdata)
                    unknown_command=False

                if play_part[1] == "reg_str":###ntcommand
                    varname = play_part[2]
                    newdata = expand_column(play_part, 3)
                    olddata=""
                    if "+" in varname:
                        # append mode
                        varname = varname.replace("+", "")
                        olddata = reg_read(varname)
                    reg_write(varname, olddata + newdata)
                    unknown_command=False

                # if play_part[1] == "shadow_setvalue":###ntcommand
                #     shadow_element_id = play_part[2]
                #     data_to_set = expand_column(play_part, 3)
                #     shadow_element = driver.execute_script('this.shadowRoot.getElementById(arguments[0]).value = arguments[1];', shadow_element_id, data_to_set)
                #     unknown_command=False

                # if play_part[1] == "a":###ntcommand
                #     varname = play_part[2]
                #     res="\n".join(get_all_a_href())
                #     reg_write(varname, res)
                #     unknown_command=False


            else:
                lel = None # list of elements

                if play_part[0] == "//" or type(play_part[0]) == list:
                    unknown_command=False

                    if type(play_part[0]) == list:
                        special_command = play_part[0]

                        if special_command[0] == "shadow-click":
                            current_shadow = WDW(driver=driver, timeout=default_wait).until(lambda x: x.find_elements(BY.XPATH, special_command[1]))[0]
                            shadow0_id = current_shadow.get_attribute("id")

                            # import selenium.webdriver.remote.shadowroot
                            # current_shadow_shadowRoot: selenium.webdriver.remote.shadowroot.ShadowRoot

                            if len(special_command) == 3:
                                # cmd, shadow0, leaf-in-0
                                special_target = driver.execute_script("return document.querySelector('#%s').shadowRoot.querySelector(arguments[0])" % shadow0_id, special_command[2])
                                logging.info("Special Target is: %s" % special_target)
                                special_target.click()


                else:
                    if not play_part[0].startswith("css:"):
                        if wait_lel_clickable:
                            wait_lel_clickable = False
                            if play_part[0].startswith("id:"):
                                target_id = play_part[0][3:]
                                #EC.element_to_be_clickable
                                lel = WDW(driver=driver, timeout=default_wait).until(EC.element_to_be_clickable((BY.ID, target_id)))
                            else:
                                lel = WDW(driver=driver, timeout=default_wait).until(EC.element_to_be_clickable((BY.XPATH, play_part[0])))
                        else:
                            if play_part[0].startswith("id:"):
                                target_id = play_part[0][3:]
                                lel = WDW(driver=driver, timeout=default_wait).until(lambda x: x.find_elements(BY.ID, target_id))
                            else:
                                lel = WDW(driver=driver, timeout=default_wait).until(lambda x: x.find_elements(BY.XPATH, play_part[0]))
                    else:
                        #https://stackoverflow.com/questions/67133483/accessing-shadowroot-via-selenium-in-firefox-returns-javascriptexception-cyclic
                        lel = driver.find_elements(BY.CSS_SELECTOR, play_part[0][4:]) # strip off initial "css:"

                    # if play_part[1] == "a":###tcommand
                    #     varname = play_part[2]
                    #     res="\n".join(get_all_a_href(beneath=lel[0]))
                    #     reg_write(varname, res)
                    #     unknown_command=False

                    if play_part[1] == "input_type": ###tcommand
                        input_caption = expand_column(play_part, 2)
                        print("*"*68)
                        print("** %s" % input_caption)
                        print("*"*68)
                        print()
                        input_data = input("$ ").strip().split("\n")[0].strip()
                        print()
                        print("*"*68)
                        lel[0].send_keys(input_data)
                        unknown_command=False

                    if play_part[1] == "enter": ###tcommand
                        lel[0].send_keys("\r")
                        unknown_command=False

                    if play_part[1] == "input_password_type": ###tcommand
                        input_caption = expand_column(play_part, 2)
                        print("*"*68)
                        print("** %s" % input_caption)
                        print("*"*68)
                        print()
                        input_data = getpass.getpass()
                        print()
                        print("*"*68)
                        lel[0].send_keys(input_data)
                        unknown_command=False

                    if play_part[1] == "submit": ###tcommand
                        lel[0].submit()
                        unknown_command=False

                    if play_part[1] == "input_setvalue": ###tcommand
                        input_caption = expand_column(play_part, 2)
                        print("*"*68)
                        print("** %s" % input_caption)
                        print("*"*68)
                        print()
                        input_data = input("$ ").strip().split("\n")[0].strip()
                        print()
                        print("*"*68)
                        driver.execute_script("arguments[0].value = arguments[1];", lel[0], input_data)
                        unknown_command=False

                    if play_part[1] == ".remove()": ###tcommand
                        driver.execute_script("arguments[0].remove();", lel[0])
                        unknown_command=False

                    if play_part[1] == "input_password_setvalue": ###tcommand
                        input_caption = expand_column(play_part, 2)
                        print("*"*68)
                        print("** %s" % input_caption)
                        print("*"*68)
                        print()
                        input_data = getpass.getpass()
                        print()
                        print("*"*68)
                        driver.execute_script("arguments[0].value = arguments[1];", lel[0], input_data)
                        unknown_command=False

                    if play_part[1] == "reg_dom":###tcommand
                        varname = play_part[2]
                        olddata=""
                        if "+" in varname:
                            # append mode
                            varname = varname.replace("+", "")
                            olddata = reg_read(varname)
                        reg_write(varname, olddata + lel[0].get_attribute("innerHTML"))
                        unknown_command=False

                    if play_part[1] == "attribute_setenv":###tcommand
                        attribute_name = play_part[2]
                        env_key = play_part[3]
                        envdata[env_key] = lel[0].get_attribute(attribute_name)
                        unknown_command=False

                    if play_part[1] == "reg_dom1":###tcommand
                        varname = play_part[2]
                        reg_write(varname, lel[0].get_attribute("innerHTML").replace("><", ">\n<"))
                        unknown_command=False

                    if play_part[1] == "reg_attr":###tcommand
                        attrname = play_part[2]
                        varname = play_part[3]
                        res=str(lel[0].get_attribute(attrname))
                        reg_write(varname, res)
                        unknown_command=False

                    if play_part[1] == "del":###tcommand
                        for del_element in lel:
                            driver.execute_script("arguments[0].remove();", del_element)
                            time.sleep(1);
                        unknown_command=False

                    if play_part[1] == "siv":###tcommand
                        driver.execute_script("arguments[0].scrollIntoView(false);", lel[0])
                        time.sleep(1);
                        unknown_command=False

                    if play_part[1] == "type": ###tcommand
                        content = expand_column(play_part, 2)
                        # content = play_part[2]
                        # if ppl > 3:
                        #     content = content_provider_facade(content, play_part[3])
                        if driver_mode.upper().find("CHROME") >= 0:
                            logging.warn("You are using send_keys (dcx:type) for chrome which may lead to unwanted form submits - consider dcx:setvalue instead.")
                        lel[0].send_keys(content)
                        unknown_command=False

                    # kind of "clear and silent type"
                    if play_part[1] == "setvalue": ###tcommand
                        content = expand_column(play_part, 2)
                        # content = play_part[2]
                        # if ppl > 3:
                        #     content = content_provider_facade(content, play_part[3])
                        #lel[0].send_keys(content)
                        driver.execute_script("arguments[0].value = arguments[1];", lel[0], content)
                        unknown_command=False

                    if play_part[1] == "click": ###tcommand
                        lel[0].click()
                        unknown_command=False

                    if play_part[1] == "checked": ###tcommand
                        if lel[0].is_selected() == False:
                            lel[0].click()
                        unknown_command=False

                    if play_part[1] == "checkedjs": ###tcommand
                        driver.execute_script("arguments[0].checked = true;", lel[0])
                        unknown_command=False

                    if play_part[1] == "uncheckedjs": ###tcommand
                        driver.execute_script("arguments[0].checked = false;", lel[0])
                        unknown_command=False

                    if play_part[1] == "unchecked": ###tcommand
                        if lel[0].is_selected() == True:
                            lel[0].click()
                        unknown_command=False

                    if play_part[1] == "clickif": ###tcommand
                        e_type = play_part[2]
                        e_contains = play_part[3]
                        constructed_xpath = "//%s[contains(., \"%s\")]" % (e_type, e_contains)
                        sub_lel = lel[0].find_elements(BY.XPATH, constructed_xpath)
                        if sub_lel is None or len(sub_lel) == 0:
                            logging.info("clickif empty")
                        else:
                            sub_lel[0].click()
                        #any_lel = WDW(driver=driver, timeout=default_wait).until(lambda x: x.find_elements(BY.XPATH, constructed_xpath))
                        unknown_command=False


                    if play_part[1] == "checked01": ###tcommand
                        varname = play_part[2]
                        if lel[0].is_selected():
                            reg_write(varname, '1')
                        else:
                            reg_write(varname, '0')
                        logging.info("REG: %s = %s" % (varname, reg_read(varname)))
                        unknown_command=False

                    if play_part[1] == "clear": ###tcommand
                        lel[0].clear()
                        unknown_command=False
            
            if unknown_command:
                raise Exception("Command '%s' is unknown" % play_part[1])

            #post tasks
            

            urls_after_filename = os.path.join(logdir_urls_pre_after, 'urls-%08d-after' % play_part_i)
            with open(urls_after_filename, 'w') as urls_after_filename_:
                urls_after_filename_.write("")
            try:
                with open(urls_after_filename, 'w') as urls_after_filename_:
                    urls_after_filename_.write(driver.current_url)
            except:
                pass


            # COOKIES
            step_cookiefilename = os.path.join(logdir_cookies, 'cookies-part-%08d.json' % play_part_i)
            with open(step_cookiefilename, 'w') as cfh:
                cfh.write(json.dumps(driver.get_cookies(), indent=4))
            global_cookie_latest_json_dump_filename = step_cookiefilename

            # SCREENSHOT
            viewport_png_out = os.path.join(logdir_viewport_img, 'part-%08d-out.png' % play_part_i)
            if args.no_img == False:
                driver.save_screenshot(viewport_png_out)
                REPORT['viewports_out'].append(viewport_png_out)

            if args.no_img == False:
                if callable(hasattr(driver, 'save_full_page_screenshot')): # only firefox has it
                    full_png_out = os.path.join(logdir_full_img, 'part-%08d-out.png' % play_part_i)
                    driver.save_full_page_screenshot(full_png_out)

        except Exception as exc:
            logging.error(exc)

            if args.trace:
                CONSOLE.print_exception()
            if args.debug:
                interactive_break()
            break

    

# end of for in parts...

# driver.save_screenshot("test.png")

if args.zip_profile:
    postrun_profile_zip = args.zip_profile[0]
    shutil.make_archive(postrun_profile_zip, "zip", profiledir_actual)


process_report(logbasedir)

if args.ff_auto_har:
    time.sleep(5)

if args.ff_auto_har:
    har_written_at = os.path.join(har_path, har_file) + ".har" #  thank you firefox
    old_size = -1
    har_size = 0
    while old_size != har_size:
        print(har_written_at)
        if os.path.isfile(har_written_at):
            old_size = har_size
            har_size = os.path.getsize(har_written_at)
            logging.info("HAR %d byte(s)" % har_size)
        else:
            logging.info("HAR not there yet...")
        time.sleep(5)

try:
    driver.close()
except Exception as exc:
    pass

driver.quit()
bye_to_hot()
logging.info("finished")


if args.post_bash == None:
    logging.info("no POST task")
else:
    post_task = """/bin/bash -c '%s'""" % args.post_bash[0]
    logging.info("POST task is %s" % pre_task)
    post_task_res = subprocess.check_output(post_task, shell=True, universal_newlines=True)
    logging.info("POST task output: %s" % post_task_res)

if args.log == False:
    shutil.rmtree(logbasedir)
