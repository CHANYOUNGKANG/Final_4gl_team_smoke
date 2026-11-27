package kr.co.haedeun.notice.domain;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

public interface AttachmentRepository extends JpaRepository<Attachment, Integer> {

    @Query("select a from Attachment a join fetch a.notice n where n.checkPost = false order by a.uploadedAt desc, a.id desc")
    List<Attachment> findAllPublic();
}
