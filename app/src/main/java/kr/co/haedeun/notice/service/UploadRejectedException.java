package kr.co.haedeun.notice.service;

public class UploadRejectedException extends RuntimeException {
    public UploadRejectedException(String message) {
        super(message);
    }
}
