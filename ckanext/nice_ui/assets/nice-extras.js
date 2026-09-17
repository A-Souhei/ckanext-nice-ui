/* Adds rows to the custom fields list (snippets/custom_form_fields.html).
 *
 * Rows are numbered 0..n-1 in their field names, so a new row takes the next
 * index. It is cloned from the last row, emptied, and has no remove toggle:
 * an empty pair is ignored on save anyway.
 */
this.ckan.module('nice-extras', function ($) {
  return {
    initialize: function () {
      $.proxyAll(this, /_on/);
      this.list = this.el.find('.nice-extras-list');
      this.el.find('.nice-extras-add').prop('hidden', false).on('click', this._onAdd);
    },

    _onAdd: function () {
      var rows = this.list.children();
      var next = rows.length;
      var row = rows.last().clone();

      row.removeClass('has-error');
      row.find('.nice-extras-error').remove();
      row.find('.nice-extras-remove').replaceWith('<span class="nice-extras-spacer"></span>');
      row.find('[name], [id], [for]').each(function () {
        var el = $(this);
        ['name', 'id', 'for'].forEach(function (attr) {
          var value = el.attr(attr);
          if (value) {
            el.attr(attr, value.replace(/(extras__|field-extras-)\d+/, '$1' + next));
          }
        });
      });
      row.find('input.form-control').val('');

      this.list.append(row);
      row.find('input.form-control').first().trigger('focus');
    }
  };
});
